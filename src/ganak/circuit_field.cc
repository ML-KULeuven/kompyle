// Copyright (c) 2026 Ibrahim El Kaddouri
// Licensed under apachev2

#include <memory>
#include <string>
#include <unordered_map>
#include <vector>

#include "klay/node.h"

#include "ganak/circuit_field.h"
#include "kompyle/kcircuit.h"

namespace kmpyl {
namespace {

// Collect distinct leaf literal indices reachable from `n`.
void CollectLits(klay::Node* n,
                 std::unordered_map<klay::Node*, bool>* visited,
                 std::vector<int>* out) {
  if (!visited->emplace(n, true).second) return;
  if (n->type == klay::NodeType::Leaf) {
    out->push_back(n->ix);
    return;
  }
  for (klay::Node* c : n->children) CollectLits(c, visited, out);
}

// Shannon-cofactor `n` along the literal `pos_ix`.
klay::Node* Cofactor(klay::Node* n, int pos_ix, Circuit* circuit,
                     std::unordered_map<klay::Node*, klay::Node*>* memo) {
  auto it = memo->find(n);
  if (it != memo->end()) return it->second;

  klay::Node* result = nullptr;
  switch (n->type) {
    case klay::NodeType::True:
    case klay::NodeType::False:
      result = n;
      break;
    case klay::NodeType::Leaf:
      if (n->ix == pos_ix) {
        result = circuit->true_node().get();
      } else if (n->ix == (pos_ix ^ 1)) {
        result = circuit->false_node().get();
      } else {
        result = n;
      }
      break;
    case klay::NodeType::And: {
      std::vector<klay::NodePtr> ch;
      ch.reserve(n->children.size());
      for (klay::Node* c : n->children) {
        ch.push_back(klay::NodePtr(Cofactor(c, pos_ix, circuit, memo)));
      }
      result = circuit->and_node(ch).get();
      break;
    }
    case klay::NodeType::Or: {
      std::vector<klay::NodePtr> ch;
      ch.reserve(n->children.size());
      for (klay::Node* c : n->children) {
        ch.push_back(klay::NodePtr(Cofactor(c, pos_ix, circuit, memo)));
      }
      result = circuit->or_node(ch).get();
      break;
    }
    default:
      throw std::logic_error("Cofactor: unknown node type");
  }

  (*memo)[n] = result;
  return result;
}

// ASCII tree-printer used for debugging circuits.
void PrintCircuitAscii(std::ostream& os, const klay::Node* node,
                       const std::string& prefix, bool is_last) {
  if (!node) {
    os << prefix << (is_last ? "└── " : "├── ") << "(null)\n";
    return;
  }

  const std::string connector = is_last ? "└── " : "├── ";
  const std::string child_pfx = prefix + (is_last ? "    " : "│   ");

  std::string label = node->get_label();
  switch (node->type) {
    case klay::NodeType::Leaf: {
      const int var = node->ix >> 1;
      const bool neg = node->ix & 1;
      label += neg ? "  (neg x" + std::to_string(var) + ")"
                   : "  (x" + std::to_string(var) + ")";
      break;
    }
    case klay::NodeType::True:  label += "  (T)"; break;
    case klay::NodeType::False: label += "  (F)"; break;
    default: break;
  }

  os << prefix << connector << label << "\n";

  std::size_t i = 0;
  for (auto it = node->children.begin(); it != node->children.end();
       ++it, ++i) {
    const bool last = (i + 1 == node->children.size());
    PrintCircuitAscii(os, *it, child_pfx, last);
  }
}

}  // namespace

// ---------------------------------------------------------------------------
// FCircuit
// ---------------------------------------------------------------------------

FCircuit::FCircuit(klay::Node* node, Circuit* circuit, double count)
    : circuit_(circuit), count_(count) {
  if (node->is_false()) is_zero_ = true;
  if (!node->is_true()) PushFactor(node);
}

std::unique_ptr<CMSat::Field> FCircuit::dup() const {
  auto* tn = circuit_->true_node().get();
  auto f = std::make_unique<FCircuit>(tn, circuit_, count_);
  f->factors_ = factors_;
  f->lit_to_factor_ = lit_to_factor_;
  f->is_zero_ = is_zero_;
  return f;
}

std::unique_ptr<CMSat::Field> FCircuit::add(const CMSat::Field& other) {
  const FCircuit& o = Cast(other);
  klay::Node* onode =
      circuit_->or_node({Materialise(), o.Materialise()}).get();
  auto* tn = circuit_->true_node().get();
  auto f = std::make_unique<FCircuit>(tn, circuit_, count_ + o.count_);
  f->PushFactor(onode);
  return f;
}

CMSat::Field& FCircuit::operator+=(const CMSat::Field& other) {
  const FCircuit& o = Cast(other);
  klay::Node* onode =
      circuit_->or_node({Materialise(), o.Materialise()}).get();
  factors_.clear();
  lit_to_factor_.clear();
  is_zero_ = false;
  count_ += o.count_;
  PushFactor(onode);
  return *this;
}

CMSat::Field& FCircuit::operator*=(const CMSat::Field& other) {
  const FCircuit& o = Cast(other);
  if (is_zero_) {
    count_ = 0.0;
    return *this;
  }
  if (o.is_zero_) {
    set_zero();
    return *this;
  }

  const std::size_t base = factors_.size();
  for (klay::Node* f : o.factors_) {
    if (f->is_false()) {
      set_zero();
      count_ = 0.0;
      return *this;
    }
    factors_.push_back(f);
  }
  for (const auto& [ix, idx] : o.lit_to_factor_) {
    lit_to_factor_[ix] = idx + base;
  }

  count_ *= o.count_;
  return *this;
}

CMSat::Field& FCircuit::operator-=(const CMSat::Field& other) {
  count_ -= Cast(other).count_;
  return *this;
}

CMSat::Field& FCircuit::operator/=(const CMSat::Field& other) {
  const FCircuit& o = Cast(other);
  if (o.count_ == 0.0) {
    throw std::runtime_error("FCircuit /= division by zero");
  }
  count_ /= o.count_;

  for (klay::Node* to_remove : o.factors_) {
    assert(to_remove->type == klay::NodeType::Leaf);
    if (is_zero_) return *this;

    const int pos_ix = to_remove->ix;

    auto map_it = lit_to_factor_.find(pos_ix);
    if (map_it == lit_to_factor_.end()) {
      map_it = lit_to_factor_.find(pos_ix ^ 1);
      if (map_it == lit_to_factor_.end()) continue;
    }

    const std::size_t fidx = map_it->second;
    klay::Node* factor = factors_[fidx];

    if (factor->type == klay::NodeType::Leaf) {
      factors_[fidx] = circuit_->true_node().get();
      lit_to_factor_.erase(pos_ix);
      lit_to_factor_.erase(pos_ix ^ 1);
      continue;
    }

    std::unordered_map<klay::Node*, klay::Node*> memo;
    klay::Node* cofactored = Cofactor(factor, pos_ix, circuit_, &memo);

    if (cofactored->is_false()) {
      set_zero();
      return *this;
    }

    factors_[fidx] = cofactored;
    lit_to_factor_.erase(pos_ix);
    lit_to_factor_.erase(pos_ix ^ 1);

    if (cofactored->is_true()) {
      for (auto it = lit_to_factor_.begin(); it != lit_to_factor_.end();) {
        if (it->second == fidx) {
          it = lit_to_factor_.erase(it);
        } else {
          ++it;
        }
      }
    }
  }
  return *this;
}

CMSat::Field& FCircuit::operator=(const CMSat::Field& other) {
  const FCircuit& o = Cast(other);
  circuit_ = o.circuit_;
  count_ = o.count_;
  factors_ = o.factors_;
  lit_to_factor_ = o.lit_to_factor_;
  is_zero_ = o.is_zero_;
  return *this;
}

bool FCircuit::operator==(const CMSat::Field& other) const {
  return Materialise() == Cast(other).Materialise();
}

bool FCircuit::is_one() const {
  if (is_zero_) return false;
  for (klay::Node* f : factors_) {
    if (!f->is_true()) return false;
  }
  return true;
}

std::ostream& FCircuit::display(std::ostream& os) const {
  const klay::Node* root = Materialise();
  if (!root) {
    os << "(null)";
    return os;
  }
  os << root->get_label() << "  [~" << count_ << " models]\n";

  std::size_t i = 0;
  for (auto it = root->children.begin(); it != root->children.end();
       ++it, ++i) {
    const bool last = (i + 1 == root->children.size());
    PrintCircuitAscii(os, *it, "", last);
  }
  return os;
}

void FCircuit::set_zero() {
  factors_.clear();
  lit_to_factor_.clear();
  factors_.push_back(circuit_->false_node().get());
  count_ = 0.0;
  is_zero_ = true;
}

void FCircuit::set_one() {
  factors_.clear();
  lit_to_factor_.clear();
  count_ = 1.0;
  is_zero_ = false;
}

klay::Node* FCircuit::Materialise() const {
  if (is_zero_) return circuit_->false_node().get();

  std::vector<klay::NodePtr> live;
  for (klay::Node* f : factors_) {
    if (!f->is_true()) live.push_back(f);
  }
  if (live.empty()) return circuit_->true_node().get();
  if (live.size() == 1) return live[0].get();
  return circuit_->and_node(live).get();
}

void FCircuit::PushFactor(klay::Node* n) {
  if (n->is_false()) {
    set_zero();
    return;
  }
  if (n->is_true()) return;

  const std::size_t idx = factors_.size();
  factors_.push_back(n);

  std::unordered_map<klay::Node*, bool> visited;
  std::vector<int> lits;
  CollectLits(n, &visited, &lits);
  for (int l : lits) lit_to_factor_[l] = idx;
}

// ---------------------------------------------------------------------------
// FGenCircuit
// ---------------------------------------------------------------------------

std::unique_ptr<CMSat::Field> FGenCircuit::lit_field(int dimacs_lit) const {
  return std::make_unique<FCircuit>(
      circuit_->literal_node(dimacs_lit).get(), circuit_, 1.0);
}

std::unique_ptr<CMSat::Field> FGenCircuit::zero() const {
  auto* tn = circuit_->true_node().get();
  auto f = std::make_unique<FCircuit>(tn, circuit_, 0.0);
  f->set_zero();
  return f;
}

std::unique_ptr<CMSat::Field> FGenCircuit::one() const {
  auto* tn = circuit_->true_node().get();
  return std::make_unique<FCircuit>(tn, circuit_, 1.0);
}

std::unique_ptr<CMSat::FieldGen> FGenCircuit::dup() const {
  return std::make_unique<FGenCircuit>(circuit_);
}

bool FGenCircuit::larger_than(const CMSat::Field& a,
                              const CMSat::Field& b) const {
  return static_cast<const FCircuit&>(a).get_count() >
         static_cast<const FCircuit&>(b).get_count();
}

}  // namespace kmpyl
