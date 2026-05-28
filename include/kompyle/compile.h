// Copyright (c) 2026 Ibrahim El Kaddouri
// Licensed under apachev2
//
// Top-level entry points for compiling formulas into klay circuits
// and for counting models without circuit construction.
//
// The Compile* functions take a non-null `Circuit*` and a description
// of the formula (a path to a CNF file, a path to a BC gate-formula
// file, or an in-memory `GatedFormula`), and they return the root
// `klay::Node*` of the compiled DNNF. The returned pointer is *owned
// by* `circuit`, it is invalidated when `circuit` is destroyed.
//
// The Count* functions take the same options and run the same DPLL
// search internally, the only difference is that they accumulate a
// model count instead of building klay nodes.

#ifndef INCLUDE_KOMPYLE_COMPILE_H_
#define INCLUDE_KOMPYLE_COMPILE_H_

#include <string>

#include <boost/multiprecision/gmp.hpp>

#include "klay/node.h"
#include "kompyle/kcircuit.h"
#include "kompyle/gated_formula.h"
#include "kompyle/options.h"


namespace kmpyl {

// Compiles the DIMACS CNF at `cnf_file` using Ganak.
// `circuit` must be non-null.
// `cnf_file` must be a path to a readable unweighted, non-projected DIMACS CNF.
//
// When `arjun_opts` is set, an Arjun independent-support minimisation
// pre-pass runs before Ganak and the simplified CNF is handed to the
// counter. When `arjun_opts` is `std::nullopt`, Ganak
// operates directly on the original CNF.
//
// Returns the root of the compiled DNNF.
klay::Node* CompileFromCnfUsingGanak(
    Circuit* circuit,
    const std::string& cnf_file,
    const GanakOptions& ganak_opts,
    const ArjunOptions& arjun_opts);

// Counts the DIMACS CNF at `cnf_file` using Ganak.
// `cnf_file` must be a path to a readable DIMACS CNF.
//
// When `arjun_opts` is set, an Arjun independent-support minimisation
// pre-pass runs before Ganak and the simplified CNF is handed to the
// counter. When `arjun_opts` is `std::nullopt`, Ganak
// operates directly on the original CNF.
//
// Returns the model count of `cnf_file`.
boost::multiprecision::mpz_int CountFromCnfUsingGanak(
    const std::string& cnf_file,
    const GanakOptions& ganak_opts,
    const ArjunOptions& arjun_opts,
    bool weighted_counting = false);

// Compiles the DIMACS CNF at `cnf_file` using d4v2.
//
// `circuit` must be non-null.
// `cnf_file` must be unweighted and not projected.
//
// Returns the root of the compiled DNNF.
klay::Node* CompileFromCnfUsingD4v2(Circuit* circuit,
                                    const std::string& cnf_file,
                                    const D4Options& opts);


// Counts models of the DIMACS CNF at `cnf_file` using d4v2.
// `cnf_file` must be a path to a readable DIMACS CNF.
//
// Returns the model count of `cnf_file`.
boost::multiprecision::mpz_int CountFromCnfUsingD4v2(
    const std::string& cnf_file,
    const D4Options& opts);


// Compiles a BC-S1.2 gate-formula file at `bc_file` using d4v2.
//
// `circuit` must be non-null. The file must consist of `I`, `G`, and
// `T` lines per the BC-S1.2 spec. comment lines start with `c` and are
// ignored.
klay::Node* CompileFromGatesFileUsingD4v2(Circuit* circuit,
                                          const std::string& bc_file,
                                          const D4Options& opts);


// Compiles an in-memory `GatedFormula` using d4v2.
//
// `circuit` and `gformula` must both be non-null. Variable names in
// `gformula` are resolved against `circuit`'s name map, so re-using the
// same formula with a different circuit is well-defined.
klay::Node* CompileFromGatesFormulaUsingD4v2(Circuit* circuit,
                                             const GatedFormula* gformula,
                                             const D4Options& opts);

}  // namespace kmpyl

#endif  // INCLUDE_KOMPYLE_COMPILE_H_
