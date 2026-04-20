// Copyright (c) 2026 Ibrahim El Kaddouri
// Licensed under apachev2

#pragma once

#include <klay/circuit.h>
#include <klay/node.h>

#include <vector>
#include <boost/multiprecision/gmp.hpp>
#include <md4/methods/nnf/Node.hpp>
#include <md4/methods/OperationManager.hpp>

namespace kmpyl {

// NOTE(Ibrahim):
// see d4/methods/DecisionDNNFOperation.hpp
template <class T>
class KlayCircuitOperation : public d4::Operation<T, klay::Node*> {
 public:
  KlayCircuitOperation() = delete;

  explicit KlayCircuitOperation(Circuit* circ) {
    circ_ = circ;
  }

  explicit KlayCircuitOperation(Circuit* circ,
                                std::vector<uint8_t> is_gate_var) {
    circ_ = circ;
    is_gate_var_ = std::move(is_gate_var);
  }

  ~KlayCircuitOperation() override = default;

  klay::Node* createTop() override {
    return circ_->true_node().get();
  }

  klay::Node* createBottom() override {
    return circ_->false_node().get();
  }

  klay::Node* manageBottom() override {
    return createBottom();
  }

  klay::Node* manageTop(std::vector<d4::Var>&) override {
    return createTop();
  }

  klay::Node* manageBranch(d4::DataBranch<klay::Node*>& e) override {
    return wrapBranch(e);
  }

  klay::Node* manageDeterministOr(d4::DataBranch<klay::Node*>* elts,
                                  unsigned size) override {
    assert(size != 0);
    if (size == 1) return wrapBranch(elts[0]);

    std::vector<klay::NodePtr> branches;
    branches.reserve(size);
    for (unsigned i = 0; i < size; i++)
      branches.push_back(klay::NodePtr(wrapBranch(elts[i])));

    return circ_->or_node(branches).get();
  }

  klay::Node* manageDecomposableAnd(klay::Node** elts, unsigned size) override {
    std::vector<klay::NodePtr> parts;
    parts.reserve(size);
    for (unsigned i = 0; i < size; i++)
      if (!elts[i]->is_true()) parts.push_back(klay::NodePtr(elts[i]));

    if (parts.empty()) return createTop();
    if (parts.size() == 1) return parts[0].get();
    return circ_->and_node(parts).get();
  }

  // NOTE(Ibrahim):
  // not really needed.
  T count(klay::Node*&) override {
    return T(0);
  }

  // NOTE(Ibrahim):
  // not really needed.
  T count(klay::Node*&, std::vector<d4::Lit>&) override {
    return T(0);
  }

 private:
  int d4lit_to_dimacs(d4::Lit l) {
    return l.sign() ? -l.var() : l.var();
  }

  klay::NodePtr makeTautology(d4::Var v) {
    int dimacs_var = static_cast<int>(v);
    std::vector<klay::NodePtr> lits;
    lits.push_back(circ_->literal_node(dimacs_var));
    lits.push_back(circ_->literal_node(-dimacs_var));
    return circ_->or_node(lits);
  }

  klay::Node* wrapBranch(d4::DataBranch<klay::Node*>& b) {
    std::vector<klay::NodePtr> parts;
    parts.reserve(b.freeVars.size() + b.unitLits.size() + 1);

    // NOTE(Ibrahim):
    // if unit lit is not a input variable, then insert `True` instead!
    // in order to avoid gate variables in the klay circuit.
    for (auto& l : b.unitLits) {
      if (!is_gate_var_.empty() && is_gate_var_[l.var()])
        parts.push_back(circ_->true_node());
      else
        parts.push_back(circ_->literal_node(d4lit_to_dimacs(l)));
    }

    // NOTE(Ibrahim):
    // If true, skip this condition in the AND node.
    // Although, klay already does this as well...
    parts.push_back(klay::NodePtr(b.d));

    // NOTE(Ibrahim):
    // option to skip free variables ?
    // makes circuit bigger, only for smoothness, which isn't always needed
    for (auto& v : b.freeVars) {
      if (!is_gate_var_.empty() && is_gate_var_[v])
        continue;
      parts.push_back(makeTautology(v));
    }

    if (parts.empty()) return createTop();

    // NOTE(Ibrahim):
    // avoid dummy AND node:
    // although it wll be re-added in klay...
    // if (parts.size() == 1) return parts[0].get();
    return circ_->and_node(parts).get();
  }

  Circuit* circ_;
  std::vector<uint8_t> is_gate_var_;
};

}  // namespace kmpyl
