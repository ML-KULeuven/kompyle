#pragma once

#include <cryptominisat5/solvertypesmini.h>
#include <klay/circuit.h>

#include <memory>
#include <string>

class FCircuit final : public CMSat::Field {
 public:
  // NOTE(Ibrahim)
  // FCircuit does not own the `circ` pointer
  FCircuit(NodePtr node, Circuit* circ)
    : node_(node), circ_(circ) {}

  NodePtr get_node() const { return node_; }
  Circuit* get_circuit() const { return circ_; }

  std::unique_ptr<Field> dup() const final {
    return std::make_unique<FCircuit>(node_, circ_);
  }

  std::unique_ptr<Field> add(const Field& other) final {
    const auto& o = cast(other);
    return make(circ_->or_node({ node_, o.node_ }));
  }

  Field& operator+=(const Field& other) final {
    const auto& o = cast(other);
    node_ = circ_->or_node({ node_, o.node_ });
    return *this;
  }

  Field& operator*=(const Field& other) final {
    const auto& o = cast(other);
    node_ = circ_->and_node({ node_, o.node_ });
    return *this;
  }

  // NOTE(Ibrahim)
  // not needed for circuits, treat as no-op
  Field& operator-=(const Field&) final { return *this; }

  // NOTE(Ibrahim)
  // not needed for circuits, treat as no-op
  Field& operator/=(const Field&) final { return *this; }

  Field& operator=(const Field& other) final {
    node_ = cast(other).node_;
    circ_ = cast(other).circ_;
    return *this;
  }

  bool operator==(const Field& other) const final {
    return node_ == cast(other).node_;
  }

  bool is_zero() const final {
    return node_.get() && node_.get()->is_false();
  }

  bool is_one()  const final {
    return node_.get() && node_.get()->is_true();
  }

  void set_zero() final { node_ = circ_->false_node(); }
  void set_one()  final { node_ = circ_->true_node();  }

  std::ostream& display(std::ostream& os) const final {
    if (node_.get())
      os << node_.get()->get_label();
    else
      os << "null";
    return os;
  }

  uint64_t bytes_used() const final {
    // NOTE(Ibrahim): Circuit size not included
    return sizeof(FCircuit);
  }

  bool parse(const std::string&, const uint32_t) final {
    // NOTE(Ibrahim): Circuit size not included
    return false;
  }

 private:
  static const FCircuit& cast(const Field& f) {
    return static_cast<const FCircuit&>(f);
  }

  std::unique_ptr<Field> make(NodePtr n) const {
    return std::make_unique<FCircuit>(n, circ_);
  }

  NodePtr  node_;
  Circuit* circ_;
};

class FGenCircuit final : public CMSat::FieldGen {
 public:
  // NOTE(Ibrahim)
  // FGenCircuit does not own the `circ` pointer
  explicit FGenCircuit(Circuit* circ) : circ_(circ) {}

  Circuit* get_circuit() { return circ_; }

  std::unique_ptr<CMSat::Field> 
    lit_field(int dimacs_lit) const {
      return std::make_unique<FCircuit>(
          circ_->literal_node(dimacs_lit), circ_);
  }

  std::unique_ptr<CMSat::Field> 
    free_var_field(int var) const {
      NodePtr pos = circ_->literal_node(+var);
      NodePtr neg = circ_->literal_node(-var);
      return std::make_unique<FCircuit>(
          circ_->or_node({ pos, neg }), circ_);
  }

  std::unique_ptr<CMSat::Field> zero() const final {
    return std::make_unique<FCircuit>(
        circ_->false_node(), circ_);
  }

  std::unique_ptr<CMSat::Field> one() const final {
    return std::make_unique<FCircuit>(
        circ_->true_node(), circ_);
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
    // implied ordering from pointer addresses ?
    // const auto& ac = static_cast<const FCircuit&>(a);
    // const auto& bc = static_cast<const FCircuit&>(b);
    // return ac.get_node().as_int() > bc.get_node().as_int();
    return false;
  }

  bool weighted() const final { return true; }

 private:
  Circuit* circ_;
};
