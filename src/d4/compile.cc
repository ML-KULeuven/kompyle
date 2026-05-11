// Copyright (c) 2026 Ibrahim El Kaddouri
// Licensed under apachev2

#include "kompyle/compile.h"

#include <cstdio>
#include <iostream>
#include <numeric>
#include <string>
#include <utility>
#include <vector>

#include "klay/node.h"
#include "md4/configurations/ConfigurationDpllStyleMethod.hpp"
#include "md4/methods/DpllStyleMethod.hpp"
#include "md4/options/methods/OptionDpllStyleMethod.hpp"
#include "md4/options/preprocs/OptionPreprocManager.hpp"
#include "md4/problem/circuit/ProblemManagerCircuit.hpp"
#include "md4/problem/cnf/ProblemManagerCnf.hpp"

#include "kompyle/kcircuit.h"
#include "kompyle/gated_formula.h"
#include "kompyle/options.h"
#include "d4/circuit_operation.h"

namespace kmpyl {
namespace {

// ---------------------------------------------------------------------------
// D4Options
// ---------------------------------------------------------------------------

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

// ---------------------------------------------------------------------------
// Config builder for CNF problems
// ---------------------------------------------------------------------------

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
// Problem-manager helpers
// ---------------------------------------------------------------------------

void InitPmWeights(d4::ProblemManagerCircuit* pm, int nb_vars) {
  pm->setNbVar(nb_vars);

  auto& wl = pm->getWeightLit();
  wl.assign((nb_vars + 1) << 1, d4::mpz::mpf_float(1));

  auto& wv = pm->getWeightVar();
  wv.assign(nb_vars + 1, d4::mpz::mpf_float(2));

  auto& ord = pm->getOrder();
  ord.resize(nb_vars + 1);
  std::iota(ord.begin(), ord.end(), 0);
}

d4::Lit ResolveToken(Circuit* circuit, const std::string& tok) {
  assert(!tok.empty());
  const bool neg = (tok[0] == '-');
  const std::string name = neg ? tok.substr(1) : tok;
  const int var = circuit->get_lit(name);
  auto l = d4::Lit::makeLitTrue(var);
  return neg ? ~l : l;
}

void MaterialiseFormula(const GatedFormula& gf, Circuit* circuit,
                        d4::ProblemManagerCircuit* pm) {
  for (const auto& g : gf.gates()) {
    if (g.kind == GatedFormula::GateKind::kTarget) {
      pm->getTrueLiterals().push_back(ResolveToken(circuit, g.output));
      continue;
    }

    d4::BcGate out;
    switch (g.kind) {
      case GatedFormula::GateKind::kAnd:
        out.gate_type = d4::BcGateType::AND;
        break;
      case GatedFormula::GateKind::kOr:
        out.gate_type = d4::BcGateType::OR;
        break;
      case GatedFormula::GateKind::kIdentity:
        out.gate_type = d4::BcGateType::IDENTITY;
        break;
      case GatedFormula::GateKind::kTarget:
        // unreachable, handled above
        break;
    }
    out.output = ResolveToken(circuit, g.output);
    out.input.reserve(g.inputs.size());
    for (const auto& tok : g.inputs) {
      out.input.push_back(ResolveToken(circuit, tok));
    }
    pm->getGates().push_back(std::move(out));
  }
}

std::vector<uint8_t> BuildExclusionMask(d4::ProblemManagerCircuit* pm) {
  if (!pm) return {};
  const int nb_vars = pm->getNbVar();
  std::vector<uint8_t> is_excluded(nb_vars + 1, true);
  for (auto& g : pm->getGates()) {
    if (g.gate_type == d4::BcGateType::IDENTITY) {
      assert(g.output.var() <= nb_vars);
      is_excluded[g.output.var()] = false;
    }
  }
  return is_excluded;
}

GatedFormula ParseBcFile(const std::string& bc_path) {
  std::ifstream in(bc_path);
  if (!in.is_open()) {
    throw std::runtime_error("cannot open: " + bc_path);
  }

  GatedFormula gf;
  std::string line;
  std::string token;
  while (std::getline(in, line)) {
    if (line.empty() || line[0] == 'c') continue;

    if (line[0] == 'I') {
      std::istringstream ss(line);
      ss >> token;  // 'I'
      ss >> token;  // varname
      gf.add_input(token);

    } else if (line[0] == 'T') {
      std::istringstream ss(line);
      ss >> token;  // 'T'
      ss >> token;  // [-]varname
      gf.add_target(token);

    } else if (line[0] == 'G') {
      std::istringstream ss(line);
      ss >> token;  // 'G'
      std::string gate_name;
      ss >> gate_name;
      ss >> token;  // ':='
      ss >> token;  // 'A' or 'O'
      const char gate_type = token[0];

      std::vector<std::string> inputs;
      while (ss >> token) inputs.push_back(token);

      if (gate_type == 'A') {
        gf.add_and(gate_name, inputs);
      } else {
        gf.add_or(gate_name, inputs);
      }

    } else {
      throw std::runtime_error(
          "CompileFromGatesFileUsingD4v2: unknown line in bc file: " + line);
    }
  }
  return gf;
}

// RAII guard that redirects stdout to /dev/null for the lifetime of the
// object. d4v2 is chatty and we don't want its output on Python stdout.
class StdoutSilencer {
 public:
  StdoutSilencer()
      : saved_(dup(STDOUT_FILENO)),
        devnull_(open("/dev/null", O_WRONLY)) {
    dup2(devnull_, STDOUT_FILENO);
  }

  ~StdoutSilencer() {
    std::fflush(stdout);
    dup2(saved_, STDOUT_FILENO);
    close(devnull_);
    close(saved_);
  }

  StdoutSilencer(const StdoutSilencer&) = delete;
  StdoutSilencer& operator=(const StdoutSilencer&) = delete;

 private:
  int saved_;
  int devnull_;
};

}  // namespace

// ---------------------------------------------------------------------------
// CompileFromCnfUsingD4v2
// ---------------------------------------------------------------------------
// See demo/competition/src/Main.cpp and demo/counter/src/Main.cpp in d4v2.

klay::Node* CompileFromCnfUsingD4v2(Circuit* circuit,
                                    const std::string& cnf_file,
                                    const D4Options& opts) {
  StdoutSilencer silencer;

  auto* init_problem = new d4::ProblemManagerCnf(cnf_file);
  assert(init_problem);

  // if (init_problem->isFloat()) {
  //   throw std::runtime_error(
  //       "This library constructs circuits from cnf files, "
  //       "provide unweighted cnf files.");
  // }
  // if (init_problem->getSelectedVar().size()) {
  //   throw std::runtime_error(
  //       "This library constructs circuits from cnf files, "
  //       "provide unprojected cnf files.");
  // }

  d4::ConfigurationPeproc preproc_config =
      MakePreprocConfig(opts, d4::PB_CNF);

  using MM = d4::MethodManager;
  auto* problem = MM::runPreproc(preproc_config, init_problem, std::cout);
  assert(problem);

  auto* klay_op = new KlayCircuitOperation<d4::mpz::mpz_int>(circuit);

  d4::ConfigurationDpllStyleMethod config;
  config.inputName          = "input constructed from python";
  config.methodName         = d4::METH_DDNNF;
  config.problemInputType   = d4::PB_CNF;
  config.operationType      = d4::OP_CUSTOM;
  config.cache              = MakeCacheConfig(opts);
  config.branchingHeuristic = MakeBranchingConfig(opts);
  config.solver.solverName  = MapSolverName(opts.solver);
  config.spec.specUpdateType = d4::SPEC_DYNAMIC;
  config.customOperation    = static_cast<void*>(klay_op);

  d4::OptionDpllStyleMethod options(config);

  using D4Method = d4::DpllStyleMethod<d4::mpz::mpz_int, klay::Node*>;
  auto* method = new D4Method(options, problem, std::cout);
  klay::Node* result = method->run();
  delete method;

  return result;
}

// ---------------------------------------------------------------------------
// CompileFromGatesFormulaUsingD4v2
// ---------------------------------------------------------------------------

klay::Node* CompileFromGatesFormulaUsingD4v2(Circuit* circuit,
                                             const GatedFormula* gformula,
                                             const D4Options& opts) {
  StdoutSilencer silencer;

  auto* init_problem = new d4::ProblemManagerCircuit();
  MaterialiseFormula(*gformula, circuit, init_problem);

  const int nb_vars = circuit->nb_vars();
  InitPmWeights(init_problem, nb_vars);

  d4::ConfigurationPeproc preproc_config;
  // Preprocessing is a no-op when using PB_CIRC.
  preproc_config.inputType = d4::PB_CIRC;

  using MM = d4::MethodManager;
  d4::ProblemManager* problem =
      MM::runPreproc(preproc_config, init_problem, std::cout);
  assert(problem);

  d4::MethodManager::displayInfoVariables(problem, std::cout);

  std::vector<uint8_t> is_gate_var = BuildExclusionMask(init_problem);

  using KlayOperation = KlayCircuitOperation<d4::mpz::mpz_int>;
  auto* klay_op = new KlayOperation(circuit, std::move(is_gate_var));

  d4::ConfigurationDpllStyleMethod config;
  config.inputName          = "input constructed from python";
  config.methodName         = d4::METH_DDNNF;
  config.problemInputType   = d4::PB_CIRC;
  config.operationType      = d4::OP_CUSTOM;
  config.cache              = MakeCacheConfig(opts);
  config.branchingHeuristic = MakeBranchingConfig(opts);
  config.solver.solverName  = MapSolverName(opts.solver);
  config.customOperation    = static_cast<void*>(klay_op);
  config.spec.removeGates   = false;
  config.spec.specUpdateType = d4::SPEC_DYNAMIC;

  d4::OptionDpllStyleMethod options(config);

  using D4Method = d4::DpllStyleMethod<d4::mpz::mpz_int, klay::Node*>;
  auto* method = new D4Method(options, problem, std::cout);
  klay::Node* result = method->run();
  delete method;

  return result;
}


// ---------------------------------------------------------------------------
// CompileFromGatesFileUsingD4v2
// ---------------------------------------------------------------------------

klay::Node* CompileFromGatesFileUsingD4v2(Circuit* circuit,
                                          const std::string& bc_file,
                                          const D4Options& opts) {
  const GatedFormula gf = ParseBcFile(bc_file);
  return CompileFromGatesFormulaUsingD4v2(circuit, &gf, opts);
}

}  // namespace kmpyl
