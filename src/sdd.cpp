// Copyright (c) 2026 Ibrahim El Kaddouri
// Licensed under apachev2

#include <stdexcept>
#include "kompyle/core.h"

Node* sdd_to_klay(SddNode* node, Circuit& circuit,
                  std::unordered_map<SddNode*, Node*>& cache) {
  auto it = cache.find(node);
  if (it != cache.end()) return it->second;

  Node* result;

  if (sdd_node_is_true(node)) {
    result = circuit.true_node().get();

  } else if (sdd_node_is_false(node)) {
    result = circuit.false_node().get();

  } else if (sdd_node_is_literal(node)) {
    SddLiteral lit = sdd_node_literal(node);
    // NOTE(Ibrahim):
    // sdd uses dimacs literals internally
    result = circuit.literal_node((int)lit).get();

  } else if (sdd_node_is_decision(node)) {
    SddNodeSize n = sdd_node_size(node);
    SddNode** elements = sdd_node_elements(node);

    std::vector<NodePtr> or_children;
    for (SddNodeSize i = 0; i < n; i++) {
      SddNode* prime = elements[2*i];
      SddNode* sub   = elements[2*i + 1];
      Node* klay_prime = sdd_to_klay(prime, circuit, cache);
      Node* klay_sub   = sdd_to_klay(sub, circuit, cache);
      NodePtr and_child = circuit.and_node({NodePtr(klay_prime), NodePtr(klay_sub)});
      or_children.push_back(and_child);
    }
    result = circuit.or_node(or_children).get();
  } else {
    // NOTE(Ibrahim):
    // doesn't happen only if you deallocate too early for example,
    // and node->type becomes garbled garbage
    std::runtime_error("Unrecognizable SddNode encountered.");
  }

  cache[node] = result;
  return result;
}


// FIXME(Ibrahim):
// pass options from python to tweak sdd manager
// see also SddCompilerOptions
// see issue: #10
Node* compile_from_sdd(Circuit* circ, SddNode* root) {
  assert(circ != nullptr);
  assert(root != nullptr);
  std::unordered_map<SddNode*, Node*> cache;
  Node* klay_root = sdd_to_klay(root, *circ, cache);
  circ->set_root(klay_root);
  return NodePtr(klay_root).get();
}


// FIXME(Ibrahim):
// pass options from python to tweak sdd manager
// see also SddCompilerOptions
// see issue: #10
Node* compile_from_cnf_using_sdd(Circuit* circ, const std::string& cnf_file) {
  assert(circ != nullptr);

  SddCompilerOptions options;
  options.cnf_filename   = nullptr;
  options.dnf_filename   = nullptr;
  options.vtree_filename = nullptr;
  options.sdd_filename   = nullptr;

  options.output_vtree_filename      = nullptr;
  options.output_vtree_dot_filename  = nullptr;
  options.output_sdd_filename        = nullptr;
  options.output_sdd_dot_filename    = nullptr;

  options.minimize_cardinality = 1;

  // 'left', 'right', 'vertical', 'balanced', 'random'
  options.initial_vtree_type = (char*)"balanced";

  // if K>0: invoke vtree search every K clauses.
  // If K=0: disable vtree search.
  // By default, dynamic vtree search is enabled
  options.vtree_search_mode  = 1;

  // perform post-compilation vtree search
  options.post_search = 1;
  options.verbose = 0;

  Cnf* cnf = read_cnf(cnf_file.c_str());
  Vtree* vtree = sdd_vtree_new(cnf->var_count, options.initial_vtree_type);
  SddManager* manager = sdd_manager_new(vtree);
  // manager = sdd_manager_create(cnf->var_count, 0);
  // manager = sdd_manager_create(cnf->var_count, 1);

  sdd_manager_set_options(&options, manager);
  SddNode* root = fnf_to_sdd(cnf, manager);

  // Cnf* cnf = read_cnf(cnf_file.c_str());
  // Vtree* vtree = sdd_vtree_new(cnf->var_count, "balanced");
  // SddManager* manager = sdd_manager_new(vtree);
  // sdd_vtree_free(vtree);
  // SddNode* root = fnf_to_sdd(cnf, manager);

  // TODO(Ibrahim):
  // make it a proper cache by restricting size
  std::unordered_map<SddNode*, Node*> cache;
  Node* klay_root = sdd_to_klay(root, *circ, cache);

  sdd_manager_free(manager);
  free_fnf(cnf);

  // in python:
  // circ->set_root(klay_root);
  return klay_root;
}
