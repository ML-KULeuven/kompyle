// Copyright (c) 2026 Ibrahim El Kaddouri
// Licensed under apachev2

#include "kompyle/compile.h"

#include <cstdio>
#include <fstream>
#include <iostream>
#include <numeric>
#include <sstream>
#include <string>
#include <utility>
#include <vector>

#include <klay/node.h>
#include <md4/configurations/ConfigurationDpllStyleMethod.hpp>
#include <md4/methods/DpllStyleMethod.hpp>
#include <md4/methods/MethodManager.hpp>
#include <md4/options/methods/OptionDpllStyleMethod.hpp>
#include <md4/options/preprocs/OptionPreprocManager.hpp>
#include <md4/problem/circuit/ProblemManagerCircuit.hpp>
#include <md4/problem/cnf/ProblemManagerCnf.hpp>

#include "kompyle/kcircuit.h"
#include "kompyle/gated_formula.h"
#include "kompyle/options.h"
#include "d4/counting_operation.h"
#include "d4/counting_operation.h"
#include "d4/circuit_operation.h"
#include "d4/internal.h"

namespace kmpyl {
namespace {

using d4_internal::MakeBranchingConfig;
using d4_internal::MakeCacheConfig;
using d4_internal::MakePreprocConfig;
using d4_internal::MapSolverName;
using d4_internal::StdoutSilencer;

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


// Build a fully-populated ConfigurationDpllStyleMethod for the given
// problem-input type. The `methodName`/`operationType`/`customOperation`
// triple is left to the caller to fill.
d4::ConfigurationDpllStyleMethod MakeDpllConfig(
    const D4Options& opts, d4::ProblemInputType input_type) {
  d4::ConfigurationDpllStyleMethod cfg;
  cfg.inputName              = "input constructed from python";
  cfg.problemInputType       = input_type;
  cfg.cache                  = MakeCacheConfig(opts);
  cfg.branchingHeuristic     = MakeBranchingConfig(opts);
  cfg.solver.solverName      = MapSolverName(opts.solver);
  cfg.spec.specUpdateType    = d4::SPEC_DYNAMIC;
  return cfg;
}

}  // namespace

// ---------------------------------------------------------------------------
// CompileFromCnfUsingD4v2
// ---------------------------------------------------------------------------
// See demo/competition/src/Main.cpp and demo/compiler/src/Main.cpp in d4v2.

klay::Node* CompileFromCnfUsingD4v2(Circuit* circuit,
                                    const std::string& cnf_file,
                                    const D4Options& opts) {
  klay::Node* result = nullptr;
  {
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

    d4::ConfigurationDpllStyleMethod config = MakeDpllConfig(opts, d4::PB_CNF);
    config.methodName       = d4::METH_DDNNF;
    config.operationType    = d4::OP_CUSTOM;
    config.customOperation  = static_cast<void*>(klay_op);
    d4::OptionDpllStyleMethod options(config);

    using D4Method = d4::DpllStyleMethod<d4::mpz::mpz_int, klay::Node*>;
    auto* method = new D4Method(options, problem, std::cout);
    result = method->run();
    delete method;
  }

  // g_d4_stats_circuit.print();
  return result;
}

// ---------------------------------------------------------------------------
// CountFromCnfUsingD4v2
// ---------------------------------------------------------------------------
// See demo/counter/src/Main.cpp in d4v2.


d4::mpz::mpz_int CountFromCnfUsingD4v2(const std::string& cnf_file,
                                       const D4Options& opts) {
  using mpz_int = d4::mpz::mpz_int;
  mpz_int result = 0;

  {
    StdoutSilencer silencer;

    auto* init_problem = new d4::ProblemManagerCnf(cnf_file);
    assert(init_problem);

    d4::ConfigurationPeproc preproc_config =
        MakePreprocConfig(opts, d4::PB_CNF);

    using MM = d4::MethodManager;
    auto* problem = MM::runPreproc(preproc_config, init_problem, std::cout);
    assert(problem);

    auto* double_op = new CountingOperation();

    d4::ConfigurationDpllStyleMethod config = MakeDpllConfig(opts, d4::PB_CNF);
    // METH_DDNNF instead of METH_COUNTING to compare with CompileFromCnfUsingD4v2
    config.methodName = d4::METH_DDNNF;
    config.operationType = d4::OP_CUSTOM;
    config.customOperation  = static_cast<void*>(double_op);

    d4::OptionDpllStyleMethod options(config);

    using D4Method = d4::DpllStyleMethod<mpz_int, mpz_int>;
    auto* method = new D4Method(options, problem, std::cout);
    result = method->run();
    delete method;
  }

  // g_d4_stats_count.print();
  return result;
}


// ---------------------------------------------------------------------------
// CompileFromGatesFormulaUsingD4v2
// ---------------------------------------------------------------------------

klay::Node* CompileFromGatesFormulaUsingD4v2(Circuit* circuit,
                                             const GatedFormula* gformula,
                                             const D4Options& opts) {
  klay::Node* result = nullptr;
  {
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

    d4::ConfigurationDpllStyleMethod config = MakeDpllConfig(opts, d4::PB_CIRC);
    config.methodName        = d4::METH_DDNNF;
    config.operationType     = d4::OP_CUSTOM;
    config.customOperation   = static_cast<void*>(klay_op);
    config.spec.removeGates  = false;

    d4::OptionDpllStyleMethod options(config);

    using D4Method = d4::DpllStyleMethod<d4::mpz::mpz_int, klay::Node*>;
    auto* method = new D4Method(options, problem, std::cout);
    result = method->run();
    delete method;
  }

  // g_d4_stats_circuit.print();
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
