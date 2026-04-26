// Copyright (c) 2026 Ibrahim El Kaddouri
// Licensed under apachev2

#include <optional>
#include <string>

#include "nanobind/nanobind.h"
#include "nanobind/stl/optional.h"  // IWYU pragma: keep
#include "nanobind/stl/string.h"    // IWYU pragma: keep

#include "python/bindings.h"
#include "kompyle/gated_formula.h"
#include "kompyle/kcircuit.h"
#include "kompyle/compile.h"
#include "kompyle/options.h"

namespace kmpyl {

namespace nb = nanobind;
using nb::literals::operator""_a;

// ---------------------------------------------------------------------------
// InitCompileBindings
// ---------------------------------------------------------------------------

void InitCompileBindings(nb::module_& m) {
  // -------------------------------------------------------------------------
  // GanakOptions
  // -------------------------------------------------------------------------

  nb::class_<GanakOptions>(m, "GanakOptions",
      "Solver options forwarded to the Ganak model counter.\n\n")
    .def(nb::init<>())
    .def_rw("verb",               &GanakOptions::verb,
            "Verbosity level (0 = silent).")
    .def_rw("do_chronobt",        &GanakOptions::do_chronobt,
            "Enable chronological back-tracking in the SAT solver.")
    .def_rw("do_use_sat_solver",  &GanakOptions::do_use_sat_solver,
            "Allow Ganak to call an external SAT solver for unit propagation.")
    .def_rw("first_restart",      &GanakOptions::first_restart,
            "First restart interval (None -> Ganak built-in default).");

  // -------------------------------------------------------------------------
  // ArjunOptions
  // -------------------------------------------------------------------------

  nb::class_<ArjunOptions>(m, "ArjunOptions",
      "Configuration for the Arjun preprocessor.\n\n"
      "Pass an instance of this class as ``arjun_options`` to "
      "``compile_from_cnf_using_ganak`` to enable and tune the pre-pass.")
    .def(nb::init<>())
    .def_rw("verb",                     &ArjunOptions::verb,
            "Verbosity level (0 = silent).")
    .def_rw("do_arjun",                 &ArjunOptions::do_arjun,
            "Run the Arjun minimisation pass.")
    .def_rw("arjun_gates",              &ArjunOptions::arjun_gates,
            "Exploit detected gates during minimisation.")
    .def_rw("do_pre_backbone",          &ArjunOptions::do_pre_backbone,
            "Run a backbone computation before the main minimisation pass.")
    .def_rw("do_probe_based",           &ArjunOptions::do_probe_based,
            "Use probe-based techniques.")
    .def_rw("arjun_simp_level",         &ArjunOptions::arjun_simp_level,
            "Simplification level passed to CryptoMiniSat inside Arjun (0-3).")
    .def_rw("arjun_backw_maxc",         &ArjunOptions::arjun_backw_maxc,
            "Maximum conflict budget for the backward-minimisation oracle.")
    .def_rw("arjun_oracle_find_bins",   &ArjunOptions::arjun_oracle_find_bins,
            "Number of binary clauses the oracle may add.")
    .def_rw("arjun_cms_glob_mult",      &ArjunOptions::arjun_cms_glob_mult,
            "Global multiplier for CryptoMiniSat conflict limits.")
    .def_rw("arjun_extend_max_confl",   &ArjunOptions::arjun_extend_max_confl,
            "Maximum conflicts used when extending the independent support.")
    .def_rw("arjun_extend_ccnr",        &ArjunOptions::arjun_extend_ccnr,
            "Use CCNR during extension.")
    .def_rw("arjun_autarkies",          &ArjunOptions::arjun_autarkies,
            "Apply autarky reasoning.")
    .def_rw("do_puura",                 &ArjunOptions::do_puura,
            "Run the PUURA elimination-to-file post-processing step.")
    .def_rw("arjun_further_min_cutoff", &ArjunOptions::arjun_further_min_cutoff,
            "Minimum number of sampling variables before PUURA is attempted.")
    .def_rw("num_threads",              &ArjunOptions::num_threads,
            "Number of threads for Arjun (1 = single-threaded).")
    .def_rw("strip_opt_indep",          &ArjunOptions::strip_opt_indep,
            "Strip optional independent variables.")
    .def_rw("all_indep",                &ArjunOptions::all_indep,
            "Treat the full variable set as independent.");

  // -------------------------------------------------------------------------
  // D4Options
  // -------------------------------------------------------------------------

  nb::enum_<D4PreprocMethod>(m, "D4PreprocMethod",
      "Pre-processing method used by d4v2 before DNNF compilation.")
    .value("Equiv",    D4PreprocMethod::kEquiv)
    .value("Backbone", D4PreprocMethod::kBackbone)
    .value("Vivi",     D4PreprocMethod::kVivi)
    .value("OccElim",  D4PreprocMethod::kOccElim)
    .value("Comb",     D4PreprocMethod::kComb)
    .value("Basic",    D4PreprocMethod::kBasic)
    .export_values();

  nb::enum_<D4Solver>(m, "D4Solver",
      "SAT-solver back-end used by d4v2.")
    .value("glucose",  D4Solver::kGlucose)
    .value("minisat",  D4Solver::kMinisat)
    .export_values();

  nb::class_<D4Options>(m, "D4Options",
      "Solver options forwarded to the d4v2 knowledge compiler.\n\n"
      "Defaults reproduce the values previously hard-coded inside kompyle.")
    .def(nb::init<>())
    .def_rw("preproc_method",   &D4Options::preproc_method,
            "Pre-processing strategy (D4PreprocMethod enum).")
    .def_rw("preproc_nb_iter",  &D4Options::preproc_nb_iter,
            "Number of pre-processing iterations.")
    .def_rw("preproc_timeout",  &D4Options::preproc_timeout,
            "Pre-processing timeout in seconds.")
    .def_rw("freq_decay",       &D4Options::freq_decay,
            "Branching heuristic decay frequency.")
    .def_rw("solver",           &D4Options::solver,
            "SAT solver back-end (D4Solver enum).")
    .def_rw("cache_first_page", &D4Options::cache_first_page,
            "Component cache initial allocation in bytes.")
    .def_rw("cache_extra_page", &D4Options::cache_extra_page,
            "Component cache extra-page size in bytes.");

  // -------------------------------------------------------------------------
  // Compile entry points
  // -------------------------------------------------------------------------

  m.def(
      "compile_from_cnf_using_ganak",
      [](Circuit* circuit,
         const std::string& cnf_file,
         const GanakOptions& ganak_opts,
         const std::optional<ArjunOptions>& arjun_opts) -> klay::NodePtr {
        // WarnGanakUnsupportedOptions(ganak_opts);
        return CompileFromCnfUsingGanak(circuit, cnf_file,
                                        ganak_opts, arjun_opts);
      },
      "circuit"_a, "cnf_file"_a,
      "ganak_options"_a = GanakOptions{},
      "arjun_options"_a = ArjunOptions{},
      "Compile a CNF file using Ganak and add the resulting DNNF nodes into\n"
      "an existing Circuit.\n\n"
      "When ``arjun_options`` is ``None`` to skip the pre-pass and let Ganak"
      "operate directly on the CNF.\n\n"
      "Parameters\n"
      "----------\n"
      "circuit : Circuit\n"
      "    Target circuit; must be non-null.\n"
      "cnf_file : str\n"
      "    Path to a readable unweighted, non-projected DIMACS CNF file.\n"
      "ganak_options : GanakOptions, optional\n"
      "    Configuration for the Ganak counter.  Defaults reproduce the\n"
      "    previous hard-coded behaviour.\n"
      "arjun_options : ArjunOptions or None, optional\n"
      "    Configuration for the Arjun pre-pass.  ``None`` disables Arjun.");

  m.def(
      "compile_from_cnf_using_d4v2",
      [](Circuit* circuit,
         const std::string& cnf_file,
         const D4Options& opts) -> klay::NodePtr {
        return CompileFromCnfUsingD4v2(circuit, cnf_file, opts);
      },
      "circuit"_a, "cnf_file"_a, "options"_a = D4Options{},
      "Compile a CNF file using d4v2 and add the resulting DNNF nodes into\n"
      "an existing Circuit.\n\n"
      "Parameters\n"
      "----------\n"
      "circuit : Circuit\n"
      "    Target circuit.\n"
      "cnf_file : str\n"
      "    Path to a readable unweighted, non-projected DIMACS CNF file.\n"
      "options : D4Options, optional\n"
      "    Solver configuration.  Defaults reproduce the previous behaviour.");

  m.def(
      "compile_from_gates_formula_using_d4v2",
      [](Circuit* circuit,
         const GatedFormula* gf,
         const D4Options& opts) -> klay::NodePtr {
        return CompileFromGatesFormulaUsingD4v2(circuit, gf, opts);
      },
      "circuit"_a, "formula"_a, "options"_a = D4Options{},
      "Compile a programmatically-constructed GatedFormula via d4v2.\n\n"
      "Parameters\n"
      "----------\n"
      "circuit : Circuit\n"
      "    Target circuit.\n"
      "formula : GatedFormula\n"
      "    In-memory gate formula resolved against the circuit's name map.\n"
      "options : D4Options, optional\n"
      "    Solver configuration.");

  m.def(
      "compile_from_gates_file_using_d4v2",
      [](Circuit* circuit,
         const std::string& bc_file,
         const D4Options& opts) -> klay::NodePtr {
        return CompileFromGatesFileUsingD4v2(circuit, bc_file, opts);
      },
      "circuit"_a, "bc_file"_a, "options"_a = D4Options{},
      "Compile a BC-S1.2 gate-formula file via d4v2.\n\n"
      "Parameters\n"
      "----------\n"
      "circuit : Circuit\n"
      "    Target circuit.\n"
      "bc_file : str\n"
      "    Path to a BC-S1.2 file.\n"
      "options : D4Options, optional\n"
      "    Solver configuration.");
}

}  // namespace kmpyl
