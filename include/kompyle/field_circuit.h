#pragma once

#include <cassert>
#include <memory>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

#include <cryptominisat5/solvertypesmini.h>
#include <klay/circuit.h>
#include <klay/node.h>

static void collect_lits(Node* n,
                         std::unordered_map<Node*, bool>& visited,
                         std::vector<int>& out)
{
  if (!visited.emplace(n, true).second) return;
  if (n->type == NodeType::Leaf) { out.push_back(n->ix); return; }
  for (Node* c : n->children) collect_lits(c, visited, out);
}

static Node* cofactor(Node* n, int pos_ix, Circuit* circ,
                      std::unordered_map<Node*, Node*>& memo)
{
  auto it = memo.find(n);
  if (it != memo.end()) return it->second;

  Node* result;
  switch (n->type) {
  case NodeType::True:
  case NodeType::False:
    result = n;
    break;
  case NodeType::Leaf:
    if (n->ix == pos_ix)
      result = circ->true_node().get();
    else if (n->ix == (pos_ix ^ 1))
      result = circ->false_node().get();
    else
      result = n;
    break;
  case NodeType::And: {
    std::vector<NodePtr> ch;
    ch.reserve(n->children.size());
    for (Node* c : n->children)
      ch.push_back(NodePtr(cofactor(c, pos_ix, circ, memo)));
    result = circ->and_node(ch).get();
    break;
  }
  case NodeType::Or: {
    std::vector<NodePtr> ch;
    ch.reserve(n->children.size());
    for (Node* c : n->children)
      ch.push_back(NodePtr(cofactor(c, pos_ix, circ, memo)));
    result = circ->or_node(ch).get();
    break;
  }
  default:
    throw std::logic_error("cofactor: unknown node type");
  }

  memo[n] = result;
  return result;
}

static void
print_circuit_ascii(std::ostream& os,
                    const Node*   node,
                    const std::string& prefix,
                    bool is_last)
{
  if (!node) {
    os << prefix << (is_last ? "└── " : "├── ") << "(null)\n";
    return;
  }

  const std::string connector = is_last ? "└── " : "├── ";
  const std::string child_pfx = prefix  + (is_last ? "    " : "│   ");

  std::string label = node->get_label();
  switch (node->type) {
  case NodeType::Leaf: {
    int var = node->ix >> 1;
    bool neg = node->ix & 1;
    label += neg ? "  (neg x" + std::to_string(var) + ")"
                 : "  (x"     + std::to_string(var) + ")";
    break;
  }
  case NodeType::True:  label += "  (T)"; break;
  case NodeType::False: label += "  (F)"; break;
  default: break;
  }

  os << prefix << connector << label << "\n";

  std::size_t i = 0;
  for (auto it = node->children.begin();
      it != node->children.end(); ++it, ++i) {
    bool last = (i + 1 == node->children.size());
    print_circuit_ascii(os, *it, child_pfx, last);
  }
}


class FCircuit final : public CMSat::Field {
 public:
  FCircuit(Node* node, Circuit* circ, double count = 1.0)
    : circ_(circ), count_(count)
  {
    if (node->is_false()) { is_zero_ = true; }
    if (!node->is_true()) { push_factor(node); }
  }

  Node* get_node() const { return materialise(); }
  Circuit* get_circuit() const { return circ_; }
  double get_count() const { return count_; }

  std::unique_ptr<Field> dup() const final {
    auto tn = circ_->true_node().get();
    auto f = std::make_unique<FCircuit>(tn, circ_, count_);
    f->factors_ = factors_;
    f->lit_to_factor_ = lit_to_factor_;
    f->is_zero_ = is_zero_;
    return f;
  }

  std::unique_ptr<Field> add(const Field& other) final {
    const auto& o = cast(other);
    Node* onode = circ_->or_node({materialise(),o.materialise()}).get();
    auto tn = circ_->true_node().get();
    auto f = std::make_unique<FCircuit>(tn, circ_, count_ + o.count_);
    f->push_factor(onode);
    return f;
  }

  Field& operator+=(const Field& other) final {
    const auto& o = cast(other);
    Node* onode = circ_->or_node({materialise(),o.materialise()}).get();
    factors_.clear();
    lit_to_factor_.clear();
    is_zero_ = false;
    count_  += o.count_;
    push_factor(onode);
    return *this;
  }

  Field& operator*=(const Field& other) final {
    const auto& o = cast(other);
    if (is_zero_) { count_ = 0.0; return *this; }
    if (o.is_zero_) { set_zero(); return *this; }

    const size_t base = factors_.size();
    for (Node* f : o.factors_) {
      if (f->is_false()) {
        set_zero();
        count_ = 0.0;
        return *this;
      }
      factors_.push_back(f);
    }
    for (const auto& [ix, idx] : o.lit_to_factor_)
      lit_to_factor_[ix] = idx + base;

    count_ *= o.count_;
    return *this;
  }

  Field& operator-=(const Field& other) final {
    count_ -= cast(other).count_;
    return *this;
  }

  Field& operator/=(const Field& other) final {
    const auto& o = cast(other);
    if (o.count_ == 0.0)
      throw std::runtime_error("FCircuit /= division by zero");

    count_ /= o.count_;

    for (Node* to_remove : o.factors_) {
      assert(to_remove->type == NodeType::Leaf);
      if (is_zero_) return *this;

      const int pos_ix = to_remove->ix;

      auto map_it = lit_to_factor_.find(pos_ix);
      if (map_it == lit_to_factor_.end()) {
        map_it = lit_to_factor_.find(pos_ix ^ 1);
        if (map_it == lit_to_factor_.end()) continue;
      }

      const size_t fidx = map_it->second;
      Node* factor = factors_[fidx];

      if (factor->type == NodeType::Leaf) {
        factors_[fidx] = circ_->true_node().get();
        lit_to_factor_.erase(pos_ix);
        lit_to_factor_.erase(pos_ix ^ 1);
        continue;
      }

      std::unordered_map<Node*, Node*> memo;
      Node* cofactored = cofactor(factor, pos_ix, circ_, memo);

      if (cofactored->is_false()) { 
        set_zero(); 
        return *this;
      }

      factors_[fidx] = cofactored;
      lit_to_factor_.erase(pos_ix);
      lit_to_factor_.erase(pos_ix ^ 1);

      if (cofactored->is_true()) {
        for (auto it = lit_to_factor_.begin(); it != lit_to_factor_.end(); ) {
          if (it->second == fidx)
            it = lit_to_factor_.erase(it);
          else
            ++it;
        }
      }
    }
    return *this;
  }

  Field& operator=(const Field& other) final {
    const auto& o = cast(other);
    circ_          = o.circ_;
    count_         = o.count_;
    factors_       = o.factors_;
    lit_to_factor_ = o.lit_to_factor_;
    is_zero_       = o.is_zero_;
    return *this;
  }

  bool operator==(const Field& other) const final {
    return materialise() == cast(other).materialise();
  }

  bool is_zero() const final {
    return is_zero_;
  }

  bool is_one() const final {
    if (is_zero_) return false;
    for (Node* f : factors_) if (!f->is_true()) return false;
    return true;
  }

  std::ostream& display(std::ostream& os) const final {
    const Node* root = materialise();
    if (!root) { os << "(null)"; return os; }

    os << root->get_label()
       << "  [~" << static_cast<long long>(count_) << " models]\n";

    std::size_t i = 0;
    for (auto it = root->children.begin(); 
        it != root->children.end(); ++it, ++i) {
      bool last = (i + 1 == root->children.size());
      print_circuit_ascii(os, *it, "", last);
    }
    return os;
  }

  void set_zero() final {
    factors_.clear();
    lit_to_factor_.clear();
    factors_.push_back(circ_->false_node().get());
    count_ = 0.0;
    is_zero_ = true;
  }

  void set_one() final {
    factors_.clear();
    lit_to_factor_.clear();
    count_ = 1.0;
    is_zero_ = false;
  }

  uint64_t bytes_used() const final { return sizeof(FCircuit); }
  bool parse(const std::string&, const uint32_t) final { return false; }

 private:
  static const FCircuit& cast(const Field& f) {
    return static_cast<const FCircuit&>(f);
  }

  Node* materialise() const {
    if (is_zero_) return circ_->false_node().get();
    std::vector<NodePtr> live;
    for (Node* f : factors_)
      if (!f->is_true()) live.push_back(f);
    if (live.empty()) return circ_->true_node().get();
    if (live.size() == 1) return live[0].get();
    return circ_->and_node(live).get();
  }

  void push_factor(Node* n) {
    if (n->is_false()) { set_zero(); return; }
    if (n->is_true()) return;

    const size_t idx = factors_.size();
    factors_.push_back(n);

    std::unordered_map<Node*, bool> visited;
    std::vector<int> lits;
    collect_lits(n, visited, lits);
    for (int l : lits) lit_to_factor_[l] = idx;
  }

  Circuit* circ_;

  // NOTE(Ibrahim):
  // double is probably not pricise enough for large counts ?
  // see `FDouble` in cryptominisat
  double count_;
  bool is_zero_ = false;
  std::vector<Node*> factors_;
  std::unordered_map<int, size_t> lit_to_factor_;
};


class FGenCircuit final : public CMSat::FieldGen {
 public:
  explicit FGenCircuit(Circuit* circ) : circ_(circ) {}

  Circuit* get_circuit() { return circ_; }

  std::unique_ptr<CMSat::Field> lit_field(int dimacs_lit) const {
    return std::make_unique<FCircuit>(
        circ_->literal_node(dimacs_lit).get(), circ_, 1.0);
  }

  std::unique_ptr<CMSat::Field> zero() const final {
    auto tn = circ_->true_node().get();
    auto f = std::make_unique<FCircuit>(tn, circ_, 0.0);
    f->set_zero();
    return f;
  }

  std::unique_ptr<CMSat::Field> one() const final {
    auto tn = circ_->true_node().get();
    return std::make_unique<FCircuit>(tn, circ_, 1.0);
  }

  std::unique_ptr<CMSat::FieldGen> dup() const final {
    return std::make_unique<FGenCircuit>(circ_);
  }

  bool larger_than(const CMSat::Field& a,
                   const CMSat::Field& b) const final {
    return static_cast<const FCircuit&>(a).get_count()
         > static_cast<const FCircuit&>(b).get_count();
  }

  bool exact() const { return false; }
  bool weighted() const final { return true; }

 private:
  Circuit* circ_;
};
