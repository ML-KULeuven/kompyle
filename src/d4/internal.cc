// Copyright (c) 2026 Ibrahim El Kaddouri
// Licensed under apachev2

#include "d4/internal.h"

#include <fcntl.h>
#include <unistd.h>

#include <cstdio>

namespace kmpyl {
namespace d4_internal {

d4::PreprocMethod MapPreprocMethod(D4PreprocMethod m) {
  switch (m) {
    case D4PreprocMethod::kEquiv:    return d4::EQUIV;
    case D4PreprocMethod::kBackbone: return d4::BACKBONE;
    case D4PreprocMethod::kVivi:     return d4::VIVI;
    case D4PreprocMethod::kOccElim:  return d4::OCC_ELIM;
    case D4PreprocMethod::kComb:     return d4::COMB;
    case D4PreprocMethod::kBasic:    return d4::BASIC;
  }
  return d4::EQUIV;  // unreachable
}

d4::SolverName MapSolverName(D4Solver s) {
  switch (s) {
    case D4Solver::kGlucose: return d4::GLUCOSE_CNF;
    case D4Solver::kMinisat: return d4::MINISAT_CNF;
  }
  return d4::GLUCOSE_CNF;  // unreachable
}

d4::ConfigurationPeproc MakePreprocConfig(const D4Options& opts,
                                          d4::ProblemInputType input_type) {
  d4::ConfigurationPeproc cfg;
  cfg.inputType     = input_type;
  cfg.nbIteration   = opts.preproc_nb_iter;
  cfg.timeout       = opts.preproc_timeout;
  cfg.preprocMethod = MapPreprocMethod(opts.preproc_method);
  return cfg;
}

d4::ConfigurationCache MakeCacheConfig(const D4Options& opts) {
  d4::ConfigurationCache cache;
  cache.isActivated           = true;
  cache.cachingMethod         = d4::CACHE_LIST;
  cache.cacheCleaningStrategy = d4::CACHE_NONE;
  cache.modeStore             = d4::CACHE_NT;
  cache.clauseRepresentation  = d4::CACHE_CLAUSE;
  cache.sizeFirstPage         = opts.cache_first_page;
  cache.sizeAdditionalPage    = opts.cache_extra_page;
  return cache;
}

d4::ConfigurationBranchingHeuristic MakeBranchingConfig(const D4Options& opts) {
  d4::ConfigurationBranchingHeuristic bh;
  bh.freqDecay              = opts.freq_decay;
  bh.scoringMethodType      = d4::SCORE_VSADS;
  bh.branchingHeuristicType = d4::BRANCHING_HYBRID_PARTIAL_CLASSIC;
  bh.phaseHeuristicType     = d4::PHASE_POLARITY;
  bh.reversePhase           = false;

  auto& poh = bh.configurationPartialOrderHeuristic;
  poh.partialOrderMethod        = d4::PARTIAL_ORDER_TREE_DECOMPOSITION;
  poh.treeDecompositionMethod   = d4::TREE_DECOMP_TREE_WIDTH;
  poh.graphExtractorMethod      = d4::GRAPH_PRIMAL;
  poh.treeDecompositionerMethod = d4::TREE_DECOMP_TOOL_FLOW_CUTTER;
  poh.useSimpGraphExtractor     = true;
  return bh;
}

// ---------------------------------------------------------------------------
// StdoutSilencer
// ---------------------------------------------------------------------------

StdoutSilencer::StdoutSilencer()
    : saved_(dup(STDOUT_FILENO)),
      devnull_(open("/dev/null", O_WRONLY)) {
  dup2(devnull_, STDOUT_FILENO);
}

StdoutSilencer::~StdoutSilencer() {
  std::fflush(stdout);
  dup2(saved_, STDOUT_FILENO);
  close(devnull_);
  close(saved_);
}

}  // namespace d4_internal
}  // namespace kmpyl
