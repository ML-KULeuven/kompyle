// Copyright (c) 2026 Ibrahim El Kaddouri
// Licensed under apachev2

#include <cassert>
#include <fcntl.h>
#include <fstream>
#include <numeric>
#include <sstream>
#include <string>
#include <unistd.h>
#include <utility>
#include <vector>

#include "kompyle/core.h"
#include "kompyle/circuit.h"
#include "kompyle/gated_formula.h"
#include "kompyle/operation_circuit.h"

#include <md4/heuristics/partialOrder/PartialOrderHeuristic.hpp>
#include <md4/problem/circuit/LitNameMap.hpp>
#include <md4/problem/circuit/ProblemManagerCircuit.hpp>
#include <md4/problem/cnf/ProblemManagerCnf.hpp>
#include <md4/options/branchingHeuristic/OptionBranchingHeuristic.hpp>
#include <md4/configurations/ConfigurationDpllStyleMethod.hpp>
#include <md4/configurations/ConfigurationPreproc.hpp>
#include <md4/methods/DpllStyleMethod.hpp>
#include <md4/methods/MethodManager.hpp>
#include <md4/options/methods/OptionDpllStyleMethod.hpp>
#include <md4/options/methods/OptionOperationManager.hpp>
#include <md4/options/preprocs/OptionPreprocManager.hpp>
#include <md4/problem/ProblemManager.hpp>
#include <md4/preprocs/PreprocManager.hpp>


namespace mpz = boost::multiprecision;
namespace kmpyl {

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

static void init_pm_weights(d4::ProblemManagerCircuit& pm, int nb_vars) {
  pm.setNbVar(nb_vars);

  auto& wl = pm.getWeightLit();
  wl.assign((nb_vars + 1) << 1, d4::mpz::mpf_float(1));

  auto& wv = pm.getWeightVar();
  wv.assign(nb_vars + 1, d4::mpz::mpf_float(2));

  auto& ord = pm.getOrder();
  ord.resize(nb_vars + 1);
  std::iota(ord.begin(), ord.end(), 0);
}


static d4::Lit resolve_token(Circuit* circ, const std::string& tok) {
  assert(!tok.empty());
  const bool neg = (tok[0] == '-');
  std::string name = neg ? tok.substr(1) : tok;
  d4::Lit l = circ->names().get_lit(name);
  return neg ? ~l : l;
}


static void
materialise_formula(const GatedFormula& gf,
                    Circuit* circ,
                    d4::ProblemManagerCircuit& pm) {
  for (const auto& g : gf.gates()) {
    if (g.kind == GatedFormula::GateKind::TARGET) {
      pm.getTrueLiterals().push_back(resolve_token(circ, g.output));
      continue;
    }

    d4::BcGate out;
    switch (g.kind) {
      case GatedFormula::GateKind::AND:
        out.gate_type = d4::BcGateType::AND;
        break;
      case GatedFormula::GateKind::OR:
        out.gate_type = d4::BcGateType::OR;
        break;
      case GatedFormula::GateKind::IDENTITY:
        out.gate_type = d4::BcGateType::IDENTITY;
        break;
      case GatedFormula::GateKind::TARGET:
        // unreachable
        break;
    }
    out.output = resolve_token(circ, g.output);
    out.input.reserve(g.inputs.size());
    for (const auto& tok : g.inputs)
      out.input.push_back(resolve_token(circ, tok));
    pm.getGates().push_back(std::move(out));
  }
}


static std::vector<uint8_t>
build_exclusion_mask(d4::ProblemManagerCircuit* pm) {
  if (!pm) return {};
  int nb_vars = pm->getNbVar();
  std::vector<uint8_t> is_excluded(nb_vars + 1, true);
  for (auto& g : pm->getGates()) {
    if (g.gate_type == d4::BcGateType::IDENTITY) {
      assert(g.output.var() <= nb_vars);
      is_excluded[g.output.var()] = false;
    }
  }
  return is_excluded;
}


static GatedFormula parse_bc_file(const std::string& bc_path) {
  std::ifstream in(bc_path);
  if (!in.is_open())
    throw std::runtime_error("cannot open: " + bc_path);

  GatedFormula gf;
  std::string line, token;
  while (std::getline(in, line)) {
    if (line.empty() || line[0] == 'c') continue;

    if (line[0] == 'I') {
      std::istringstream ss(line);
      ss >> token;          // 'I'
      ss >> token;          // varname
      gf.add_input(token);

    } else if (line[0] == 'T') {
      std::istringstream ss(line);
      ss >> token;          // 'T'
      ss >> token;          // [-]varname
      gf.add_target(token);

    } else if (line[0] == 'G') {
      std::istringstream ss(line);
      ss >> token;              // 'G'
      std::string gate_name;
      ss >> gate_name;
      ss >> token;              // ':='
      ss >> token;              // 'A' or 'O'
      char gate_type = token[0];

      std::vector<std::string> inputs;
      while (ss >> token) inputs.push_back(token);

      if (gate_type == 'A')
        gf.add_and(gate_name, inputs);
      else  // 'O'
        gf.add_or(gate_name, inputs);

    } else {
      throw std::runtime_error(
          "compile_from_gates_using_d4v2: unknown line in bc file: " + line);
    }
  }
  return gf;
}


// ---------------------------------------------------------------------------
// compile_from_cnf_using_d4v2
// ---------------------------------------------------------------------------

// NOTE(Ibrahim):
// see demo/competition/src/Main.cpp and demo/counter/src/Main.cpp in d4v2

klay::Node*
compile_from_cnf_using_d4v2(Circuit* circ, const std::string& cnf_file) {
  int saved = dup(STDOUT_FILENO);
  int devnull = open("/dev/null", O_WRONLY);
  dup2(devnull, STDOUT_FILENO);

  auto* init_problem = new d4::ProblemManagerCnf(cnf_file);
  assert(init_problem);

  if (init_problem->isFloat()) {
    throw std::runtime_error(
        "This library constructs circuits from cnf files, "
        "provide unweighted cnf files.");
  }

  if (init_problem->getSelectedVar().size()) {
    throw std::runtime_error(
        "This library constructs circuits from cnf files, "
        "provide unprojected cnf files.");
  }

  d4::ConfigurationPeproc preproc_config;
  preproc_config.inputType     = d4::PB_CNF;
  preproc_config.nbIteration   = 5;
  preproc_config.timeout       = 60;

  // FIXME(Ibrahim): SHARP_EQUIV, COMPILE_EQUIV triggers an assertion on
  // trivially-unsat problems inside d4v2's bipartition preproc. Keep
  // BASIC (i.e. no-op) until that's fixed upstream.
  preproc_config.preprocMethod = d4::SHARP_EQUIV;

  using MM = d4::MethodManager;
  auto* problem = MM::runPreproc(preproc_config, init_problem, std::cout);
  assert(problem);

  d4::ConfigurationCache cache;
  cache.isActivated           = true;
  cache.cachingMethod         = d4::CACHE_LIST;
  cache.cacheCleaningStrategy = d4::CACHE_NONE;
  cache.modeStore             = d4::CACHE_NT;
  cache.clauseRepresentation  = d4::CACHE_CLAUSE;
  cache.sizeFirstPage         = 1UL << 32;
  cache.sizeAdditionalPage    = 1UL << 29;

  d4::ConfigurationBranchingHeuristic bheuristic;
  bheuristic.freqDecay              = 2048;
  bheuristic.scoringMethodType      = d4::SCORE_VSADS;
  bheuristic.branchingHeuristicType = d4::BRANCHING_HYBRID_PARTIAL_CLASSIC;
  bheuristic.phaseHeuristicType     = d4::PHASE_POLARITY;
  bheuristic.reversePhase           = false;

  auto& poh = bheuristic.configurationPartialOrderHeuristic;

  // FIXME(Ibrahim): PARTIAL_ORDER_TREE_DECOMPOSITION triggers an assertion
  // inside d4v2. Keep NONE until that's fixed upstream.

  poh.partialOrderMethod        = d4::PARTIAL_ORDER_NONE;
  poh.treeDecompositionMethod   = d4::TREE_DECOMP_TREE_WIDTH;
  poh.graphExtractorMethod      = d4::GRAPH_PRIMAL;
  poh.treeDecompositionerMethod = d4::TREE_DECOMP_TOOL_FLOW_CUTTER;
  poh.useSimpGraphExtractor     = true;

  auto* klayOp = new KlayCircuitOperation<mpz::mpz_int>(circ);

  d4::ConfigurationDpllStyleMethod config;
  config.inputName            = "input constructed from python";
  config.methodName           = d4::METH_DDNNF;
  config.problemInputType     = d4::PB_CNF;
  config.operationType        = d4::OP_CUSTOM;
  config.cache                = cache;
  config.branchingHeuristic   = bheuristic;
  config.solver.solverName    = d4::GLUCOSE_CNF;
  config.spec.specUpdateType  = d4::SPEC_DYNAMIC;
  config.customOperation      = static_cast<void*>(klayOp);

  d4::OptionDpllStyleMethod options(config);

  using D4Method = d4::DpllStyleMethod<mpz::mpz_int, klay::Node*>;
  auto* method = new D4Method(options, problem, std::cout);

  klay::Node* result = method->run();

  delete method;

  fflush(stdout);
  dup2(saved, STDOUT_FILENO);
  close(devnull);
  close(saved);

  return result;
}


// ---------------------------------------------------------------------------
// compile_from_gates_using_d4v2 - BC-file
// ---------------------------------------------------------------------------

klay::Node*
compile_from_gates_using_d4v2(Circuit* circ, const std::string& bc_file) {
  GatedFormula gf = parse_bc_file(bc_file);
  return compile_from_gates_using_d4v2(circ, &gf);
}


// ---------------------------------------------------------------------------
// compile_from_gates_using_d4v2 - GatedFormula overload
// ---------------------------------------------------------------------------

klay::Node*
compile_from_gates_using_d4v2(Circuit* circ, const GatedFormula* gf) {
  int saved = dup(STDOUT_FILENO);
  int devnull = open("/dev/null", O_WRONLY);
  dup2(devnull, STDOUT_FILENO);

  auto* init_problem = new d4::ProblemManagerCircuit();
  materialise_formula(*gf, circ, *init_problem);

  const int nb_vars = circ->nb_vars();
  init_pm_weights(*init_problem, nb_vars);

  d4::ConfigurationPeproc preproc_config;
  preproc_config.inputType    = d4::PB_CIRC;
  preproc_config.nbIteration  = 5;
  preproc_config.timeout      = 60;

  // NOTE(Ibrahim):
  // PreprocManager::makePreprocManager defaults to PreprocBasicCircuit,
  // whose run() is a no-op. SHARP_EQUIV / COMPILE_EQUIV caused issues
  // (see compile_from_cnf_using_d4v2); stay with BASIC.
  preproc_config.preprocMethod = d4::BASIC;

  d4::ProblemManager* problem =
      d4::MethodManager::runPreproc(preproc_config, init_problem, std::cout);
  assert(problem);

  d4::MethodManager::displayInfoVariables(problem, std::cout);

  d4::ConfigurationCache cache;
  cache.isActivated           = true;
  cache.cachingMethod         = d4::CACHE_LIST;
  cache.cacheCleaningStrategy = d4::CACHE_NONE;
  cache.modeStore             = d4::CACHE_NT;
  cache.clauseRepresentation  = d4::CACHE_CLAUSE;
  cache.sizeFirstPage         = 1UL << 32;
  cache.sizeAdditionalPage    = 1UL << 29;

  d4::ConfigurationBranchingHeuristic bheuristic;
  bheuristic.freqDecay              = 2048;
  bheuristic.scoringMethodType      = d4::SCORE_VSADS;
  bheuristic.branchingHeuristicType = d4::BRANCHING_HYBRID_PARTIAL_CLASSIC;
  bheuristic.phaseHeuristicType     = d4::PHASE_POLARITY;
  bheuristic.reversePhase           = false;

  auto& poh = bheuristic.configurationPartialOrderHeuristic;
  poh.partialOrderMethod        = d4::PARTIAL_ORDER_NONE;
  poh.treeDecompositionMethod   = d4::TREE_DECOMP_TREE_WIDTH;
  poh.graphExtractorMethod      = d4::GRAPH_PRIMAL;
  poh.treeDecompositionerMethod = d4::TREE_DECOMP_TOOL_FLOW_CUTTER;
  poh.useSimpGraphExtractor     = true;

  std::vector<uint8_t> is_gate_var = build_exclusion_mask(init_problem);

  using KlayOperation = KlayCircuitOperation<mpz::mpz_int>;
  auto* klayOp = new KlayOperation(circ, std::move(is_gate_var));

  d4::ConfigurationDpllStyleMethod config;
  config.inputName            = "input constructed from python";
  config.methodName           = d4::METH_DDNNF;
  config.problemInputType     = d4::PB_CIRC;
  config.operationType        = d4::OP_CUSTOM;
  config.cache                = cache;
  config.branchingHeuristic   = bheuristic;
  config.solver.solverName    = d4::GLUCOSE_CNF;
  config.customOperation      = static_cast<void*>(klayOp);
  config.spec.removeGates     = false;
  config.spec.specUpdateType  = d4::SPEC_DYNAMIC;

  d4::OptionDpllStyleMethod options(config);

  using D4Method = d4::DpllStyleMethod<mpz::mpz_int, klay::Node*>;
  auto* method = new D4Method(options, problem, std::cout);

  klay::Node* result = method->run();

  delete method;

  fflush(stdout);
  dup2(saved, STDOUT_FILENO);
  close(devnull);
  close(saved);

  return result;
}

}  // namespace kmpyl
