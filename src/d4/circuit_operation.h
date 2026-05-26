// Copyright (c) 2026 Ibrahim El Kaddouri
// Licensed under apachev2

#ifndef SRC_D4_CIRCUIT_OPERATION_H_
#define SRC_D4_CIRCUIT_OPERATION_H_

#include <cassert>
#include <cstdint>
#include <utility>
#include <vector>

#include <klay/node.h>
#include <md4/methods/OperationManager.hpp>

#include "d4/d4_stats.h"
#include "kompyle/kcircuit.h"
#include "d4/d4_stats.h"

namespace kmpyl {

// d4v2 Operation implementation that builds a klay circuit instead of
// counting models. See md4/methods/DecisionDNNFOperation.hpp for the base
// protocol we implement.
//
// This lives in a header because it is a class template; the bodies are
// kept short so that keeping them in the class body is still reasonable.
template <class T>
class KlayCircuitOperation : public d4::Operation<T, klay::Node*> {
 public:
  KlayCircuitOperation() = delete;

  explicit KlayCircuitOperation(Circuit* circuit) : circuit_(circuit) {}

  KlayCircuitOperation(Circuit* circuit, std::vector<uint8_t> is_gate_var)
      : circuit_(circuit), is_gate_var_(std::move(is_gate_var)) {}

  ~KlayCircuitOperation() override = default;

  klay::Node* createTop() override {
    ++g_d4_stats_circuit.n_top;
    D4ScopedTimer t(g_d4_stats_circuit.ns_top);
    return circuit_->true_node().get();
  }

  klay::Node* createBottom() override {
    ++g_d4_stats_circuit.n_bottom;
    D4ScopedTimer t(g_d4_stats_circuit.ns_bottom);
    return circuit_->false_node().get();
  }

  klay::Node* manageBottom() override {
    return createBottom();
  }

  klay::Node* manageTop(std::vector<d4::Var>&) override {
    return createTop();
  }

  klay::Node* manageBranch(d4::DataBranch<klay::Node*>& e) override {
    ++g_d4_stats_circuit.n_branch;
    D4ScopedTimer t(g_d4_stats_circuit.ns_branch);
    return WrapBranch(e);
  }

  klay::Node* manageDeterministOr(d4::DataBranch<klay::Node*>* elts,
                                  unsigned size) override {
    ++g_d4_stats_circuit.n_add;
    D4ScopedTimer t(g_d4_stats_circuit.ns_add);
    assert(size != 0);
    if (size == 1) return WrapBranch(elts[0]);

    std::vector<klay::NodePtr> branches;
    branches.reserve(size);
    for (unsigned i = 0; i < size; ++i) {
      branches.push_back(klay::NodePtr(WrapBranch(elts[i])));
    }
    return circuit_->or_node(branches).get();
  }

  klay::Node* manageDecomposableAnd(klay::Node** elts,
                                    unsigned size) override {
    ++g_d4_stats_circuit.n_mul;
    D4ScopedTimer t(g_d4_stats_circuit.ns_mul);
    std::vector<klay::NodePtr> parts;
    parts.reserve(size);
    for (unsigned i = 0; i < size; ++i) {
      if (!elts[i]->is_true()) parts.push_back(klay::NodePtr(elts[i]));
    }

    if (parts.empty()) return createTop();
    if (parts.size() == 1) return parts[0].get();
    return circuit_->and_node(parts).get();
  }

  // The count() overrides are intentionally no-ops: this Operation only
  // produces circuits, never numeric counts.
  T count(klay::Node*&) override { 
    return T(0);
  }

  T count(klay::Node*&, std::vector<d4::Lit>&) override {
    return T(0);
  }

 private:
  static int D4LitToDimacs(d4::Lit l) {
    return l.sign() ? -l.var() : l.var();
  }

  klay::NodePtr MakeTautology(d4::Var v) {
    ++g_d4_stats_circuit.n_taut;
    D4ScopedTimer t(g_d4_stats_circuit.ns_taut);

    const int dimacs_var = static_cast<int>(v);
    std::vector<klay::NodePtr> lits;
    lits.push_back(circuit_->literal_node(dimacs_var));
    lits.push_back(circuit_->literal_node(-dimacs_var));
    return circuit_->or_node(lits);
  }

  klay::NodePtr MakeLiteralNode(d4::Lit l) {
    ++g_d4_stats_circuit.n_lit_node;
    D4ScopedTimer t(g_d4_stats_circuit.ns_lit_node);
    return circuit_->literal_node(D4LitToDimacs(l));
  }

  klay::Node* WrapBranch(d4::DataBranch<klay::Node*>& b) {
    std::vector<klay::NodePtr> parts;
    parts.reserve(b.freeVars.size() + b.unitLits.size() + 1);

    // If a unit literal is a gate variable, insert True instead, so gate
    // variables never appear in the klay circuit.
    for (auto& l : b.unitLits) {
      if (!is_gate_var_.empty() && is_gate_var_[l.var()]) {
        parts.push_back(circuit_->true_node());
      } else {
        // parts.push_back(circuit_->literal_node(D4LitToDimacs(l)));
        parts.push_back(MakeLiteralNode(l));
      }
    }

    // If the branch's inner node is True, klay will skip it in the AND;
    // either way it is safe to push.
    parts.push_back(klay::NodePtr(b.d));

    // Free variables contribute a tautology (v OR -v) for smoothness.
    // Skipping them would yield a smaller but non-smooth circuit.
    for (auto& v : b.freeVars) {
      if (!is_gate_var_.empty() && is_gate_var_[v]) continue;
      parts.push_back(MakeTautology(v));
    }

    if (parts.empty()) return createTop();
    return circuit_->and_node(parts).get();
  }

  Circuit* circuit_;
  std::vector<uint8_t> is_gate_var_;
};

}  // namespace kmpyl

#endif  // SRC_D4_CIRCUIT_OPERATION_H_
