// Copyright (c) 2026 Ibrahim El Kaddouri
// Licensed under apachev2

#include "ganak/circuit_field.h"

#include <stdexcept>
#include <unordered_map>
#include <vector>

#include "klay/node.h"
#include "kompyle/kcircuit.h"

namespace kmpyl {
namespace {

klay::NodePtr SubstituteTrue(klay::Node* n,
                             const std::unordered_set<int>& true_ixs,
                             Circuit* circ,
                             std::unordered_map<klay::Node*, klay::NodePtr>& memo) {
  auto it = memo.find(n);
  if (it != memo.end())
    return it->second;

  klay::NodePtr result(nullptr);
  switch (n->type) {
    case klay::NodeType::True:
    case klay::NodeType::False:
      result = klay::NodePtr(n);
      break;

    case klay::NodeType::Leaf:
      if (true_ixs.count(n->ix))
        result = circ->true_node();
      else if (true_ixs.count(n->ix ^ 1))
        result = circ->false_node();
      else
        result = klay::NodePtr(n);
      break;

    case klay::NodeType::And: {
      std::vector<klay::NodePtr> ch;
      ch.reserve(n->children.size());
      for (klay::Node* c : n->children)
        ch.push_back(SubstituteTrue(c, true_ixs, circ, memo));
      result = circ->and_node(ch);
      break;
    }

    case klay::NodeType::Or: {
      std::vector<klay::NodePtr> ch;
      ch.reserve(n->children.size());
      for (klay::Node* c : n->children)
        ch.push_back(SubstituteTrue(c, true_ixs, circ, memo));
      result = circ->or_node(ch);
      break;
    }

    default:
      throw std::logic_error("SubstituteTrue, unknown node type");
  }

  memo.emplace(n, result);
  return result;
}

}  // namespace

// ---------------------------------------------------------------------------
// FCircuit
// ---------------------------------------------------------------------------

std::unique_ptr<CMSat::Field> FCircuit::dup() const {
  ++g_gk_stats_circuit.n_dup;
  auto t0 = std::chrono::steady_clock::now();
  auto r = std::make_unique<FCircuit>(node_, circ_);
  r->val_  = val_;
  r->lits_ = lits_;
  g_gk_stats_circuit.ns_dup += (std::chrono::steady_clock::now() - t0).count();
  return r;
}

std::unique_ptr<CMSat::Field> FCircuit::add(const CMSat::Field& other) {
  ++g_gk_stats_circuit.n_add;
  auto t0 = std::chrono::steady_clock::now();
  const auto& o = cast(other);
  klay::NodePtr or_node = circ_->or_node({ node_, o.node_ });
  auto a = std::make_unique<FCircuit>(or_node, circ_, val_ + o.val_);

  a->lits_ = lits_;
  for (int ix : o.lits_)
    a->lits_.insert(ix);

  g_gk_stats_circuit.ns_add += (std::chrono::steady_clock::now() - t0).count();
  return a;
}

CMSat::Field& FCircuit::operator+=(const CMSat::Field& other) {
  ++g_gk_stats_circuit.n_add;
  auto t0 = std::chrono::steady_clock::now();
  const auto& o = cast(other);
  node_  = circ_->or_node({ node_, o.node_ });
  val_  += o.val_;

  for (int ix : o.lits_)
    lits_.insert(ix);

  g_gk_stats_circuit.ns_add += (std::chrono::steady_clock::now() - t0).count();
  return *this;
}

CMSat::Field& FCircuit::operator*=(const CMSat::Field& other) {
  ++g_gk_stats_circuit.n_mul;
  auto t0 = std::chrono::steady_clock::now();
  const auto& o = cast(other);
  node_  = circ_->and_node({ node_, o.node_ });
  val_  *= o.val_;

  for (int ix : o.lits_)
    lits_.insert(ix);

  g_gk_stats_circuit.ns_mul += (std::chrono::steady_clock::now() - t0).count();
  return *this;
}

CMSat::Field& FCircuit::operator-=(const CMSat::Field& other) {
  val_ -= cast(other).val_;
  return *this;
}

CMSat::Field& FCircuit::operator/=(const CMSat::Field& other) {
  const FCircuit& o = cast(other);
  val_ /= o.val_;

  std::unordered_map<klay::Node*, klay::NodePtr> memo;
  node_ = SubstituteTrue(node_.get(), o.lits_, circ_, memo);

  for (int ix : o.lits_) {
    lits_.erase(ix);
    lits_.erase(ix ^ 1);
  }

  return *this;
}

CMSat::Field& FCircuit::operator=(const CMSat::Field& other) {
  const FCircuit& o = cast(other);
  node_  = o.node_;
  circ_  = o.circ_;
  val_   = o.val_;
  lits_  = o.lits_;
  return *this;
}

bool FCircuit::operator==(const CMSat::Field& other) const {
  return node_ == cast(other).node_;
}

void FCircuit::set_zero() {
  val_  = 0;
  node_ = circ_->false_node();
  lits_.clear();
}

void FCircuit::set_one() {
  val_  = 1;
  node_ = circ_->true_node();
  lits_.clear();
}

std::ostream& FCircuit::display(std::ostream& os) const {
  if (node_.get()) os << node_.get()->get_label();
  else             os << "null";
  return os;
}

// ---------------------------------------------------------------------------
// FGenCircuit
// ---------------------------------------------------------------------------

std::unique_ptr<CMSat::Field> FGenCircuit::lit_field(int dimacs_lit) const {
  ++g_gk_stats_circuit.n_lit_field;
  auto t0 = std::chrono::steady_clock::now();
  auto a = std::make_unique<FCircuit>(circ_->literal_node(dimacs_lit), circ_, 1);
  a->add_lit(klay::Lit::fromInt(dimacs_lit).internal_val());
  g_gk_stats_circuit.ns_lit_field += (std::chrono::steady_clock::now() - t0).count();
  return a;
}

std::unique_ptr<CMSat::Field> FGenCircuit::zero() const {
  ++g_gk_stats_circuit.n_zero;
  auto t0 = std::chrono::steady_clock::now();
  auto a = std::make_unique<FCircuit>(circ_->false_node(), circ_, 0);
  g_gk_stats_circuit.ns_zero += (std::chrono::steady_clock::now() - t0).count();
  return a;
}

std::unique_ptr<CMSat::Field> FGenCircuit::one() const {
  ++g_gk_stats_circuit.n_one;
  auto t0 = std::chrono::steady_clock::now();
  auto a = std::make_unique<FCircuit>(circ_->true_node(), circ_, 1);
  g_gk_stats_circuit.ns_one += (std::chrono::steady_clock::now() - t0).count();
  return a;
}

std::unique_ptr<CMSat::FieldGen> FGenCircuit::dup() const {
  ++g_gk_stats_circuit.n_gen_dup;
  auto t0 = std::chrono::steady_clock::now();
  auto a = std::make_unique<FGenCircuit>(circ_);
  g_gk_stats_circuit.ns_gen_dup += (std::chrono::steady_clock::now() - t0).count();
  return a;
}

bool FGenCircuit::larger_than(const CMSat::Field& a, const CMSat::Field& b) const {
  return static_cast<const FCircuit&>(a).get_count() >
         static_cast<const FCircuit&>(b).get_count();
}

}  // namespace kmpyl
