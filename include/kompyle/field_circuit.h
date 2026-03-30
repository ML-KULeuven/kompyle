#pragma once

#include <cryptominisat5/solvertypesmini.h>
#include <klay/circuit.h>

#include <memory>
#include <string>

class FCircuit final : public CMSat::Field {
 public:
  // NOTE(Ibrahim)
  // FCircuit does not own the `circ` pointer
  FCircuit(NodePtr node, Circuit* circ, double count = 1.0)
    : node_(node), circ_(circ), count_(count) {}

  NodePtr get_node() const { return materialise(); }
  Circuit* get_circuit() const { return circ_; }
  double get_count() const { return count_; }

  void add_pending_lit(NodePtr lit) {
    pending_lits_.push_back(lit);
  }

  std::unique_ptr<Field> dup() const final {
    auto f = std::make_unique<FCircuit>(node_, circ_, count_);
    f->pending_lits_ = pending_lits_;
    return f;
  }

  std::unique_ptr<Field> add(const Field& other) final {
    const auto& o = cast(other);
    return std::make_unique<FCircuit>(
        circ_->or_node({materialise(), o.materialise()}),
        circ_, count_ + o.count_);
  }

  Field& operator+=(const Field& other) final {
    const auto& o = cast(other);
    // std::raise(SIGINT);
    node_  = circ_->or_node({materialise(), o.materialise()});
    pending_lits_.clear();
    count_ += o.count_;
    return *this;
  }

  Field& operator*=(const Field& other) final {
    const auto& o = cast(other);
    // std::raise(SIGINT);
    if (o.node_.get()->is_true() && !o.pending_lits_.empty()) {
      for (const auto& l : o.pending_lits_)
        pending_lits_.push_back(l);
    } else {
      node_ = circ_->and_node({materialise(), o.materialise()});
      pending_lits_.clear();
    }
    count_ *= o.count_;
    return *this;
  }

  Field& operator-=(const Field& other) final {
    const auto& o = cast(other);
    count_ -= o.count_;
    return *this;
  }

  Field& operator/=(const Field& other) final {
    const auto& o = cast(other);
    if (o.count_ == 0.0) throw std::runtime_error("FCircuit /= division by zero");

    // std::raise(SIGINT);
    assert((o.node_.get()->is_true() && o.pending_lits_.size() == 1));
    const NodePtr& to_remove = o.pending_lits_[0];
    auto it = std::find(pending_lits_.begin(), pending_lits_.end(), to_remove);
    assert(it != pending_lits_.end());

    pending_lits_.erase(it);
    count_ /= o.count_;
    return *this;
  }

  Field& operator=(const Field& other) final {
    const auto& o = cast(other);
    node_ = o.node_;
    circ_ = o.circ_;
    count_ = o.count_;
    pending_lits_ = o.pending_lits_;
    return *this;
  }

  bool operator==(const Field& other) const final {
    return materialise() == cast(other).materialise();
  }

  bool is_zero() const final {
    return node_.get()->is_false();
  }

  bool is_one()  const final {
    return node_.get()->is_true() && pending_lits_.empty();
  }

  std::ostream& display(std::ostream& os) const final {
    if (node_.get())
      os << node_.get()->get_label();
    else
      os << "null";
    return os;
  }

  void set_zero() final {
    node_ = circ_->false_node();
    pending_lits_.clear();
    count_ = 0.0; 
  }

  uint64_t bytes_used() const final {
    // NOTE(Ibrahim): Circuit size not included
    return sizeof(FCircuit);
  }

  void set_one()  final {
    node_ = circ_->true_node();
    pending_lits_.clear();
    count_ = 1.0;
  }

  bool parse(const std::string&, const uint32_t) final {
    // NOTE(Ibrahim): Circuit size not included
    return false;
  }

 private:
  static const FCircuit& cast(const Field& f) {
    return static_cast<const FCircuit&>(f);
  }

  NodePtr materialise() const {
    if (pending_lits_.empty()) return node_;
    std::vector<NodePtr> children(pending_lits_.begin(), pending_lits_.end());
    if (!node_.get()->is_true()) children.push_back(node_);
    if (children.size() == 1) return children[0];
    return circ_->and_node(children);
  }

  NodePtr node_;
  Circuit* circ_;
  double count_;
  std::vector<NodePtr> pending_lits_;
};

class FGenCircuit final : public CMSat::FieldGen {
 public:
  // NOTE(Ibrahim)
  // FGenCircuit does not own the `circ` pointer
  explicit FGenCircuit(Circuit* circ) : circ_(circ) {}

  Circuit* get_circuit() { return circ_; }

  std::unique_ptr<CMSat::Field> 
    lit_field(int dimacs_lit) const {
      // auto f = std::make_unique<FCircuit>(
      //          circ_->literal_node(dimacs_lit), circ_, 1.0);
      auto f = std::make_unique<FCircuit>(circ_->true_node(), circ_, 1.0);
      f->add_pending_lit(circ_->literal_node(dimacs_lit));
      return f;
  }

  std::unique_ptr<CMSat::Field> zero() const final {
    return std::make_unique<FCircuit>(
        circ_->false_node(), circ_, 0.0);
  }

  std::unique_ptr<CMSat::Field> one() const final {
    return std::make_unique<FCircuit>(
        circ_->true_node(), circ_, 1.0);
  }

  // NOTE(Ibrahim):
  // doesn't provide a deep coly nor a shallow copy!
  std::unique_ptr<CMSat::FieldGen> dup() const final {
    return std::make_unique<FGenCircuit>(circ_);
  }

  // FIXME(Ibrahim):
  // is only used in `disable_smaller_cube_if_overlap`
  // in Ganak to determine which cube to disable.
  // It should returns true if the first weight is larger.
  // Not sure why ...
  // issue:
  bool larger_than(
      const CMSat::Field& a,
      const CMSat::Field& b) const final {
    const auto& ac = static_cast<const FCircuit&>(a);
    const auto& bc = static_cast<const FCircuit&>(b);
    return ac.get_count() > bc.get_count();
  }

  bool weighted() const final { return true; }

 private:
  Circuit* circ_;
};
