// Copyright (c) 2026 Ibrahim El Kaddouri
// Licensed under apachev2

#ifndef INCLUDE_KOMPYLE_OPTIONS_H_
#define INCLUDE_KOMPYLE_OPTIONS_H_

#include <cstdint>
#include <optional>

namespace kmpyl {

// ---------------------------------------------------------------------------
// GanakPolarType
// ---------------------------------------------------------------------------

enum class GanakPolarType : int {
  // Use the solver's default (VSIDS-driven) polarity heuristic.
  kStandard    = 0,
  // Reuse the polarity stored in the component cache (usually best for
  // knowledge compilation workloads).
  kCache       = 1,
  // Always branch on the negative literal first.
  kForcedFalse = 2,
  // Always branch on the positive literal first.
  kForcedTrue  = 3,
};

// ---------------------------------------------------------------------------
// GanakOptions
// ---------------------------------------------------------------------------

struct GanakOptions {
  // Verbosity (0 = silent).
  int verb = 0;

  // Enable chronological back-tracking in the SAT solver.
  bool do_chronobt = true;

  // Allow Ganak to call an external SAT solver for unit propagation.
  bool do_use_sat_solver = true;

  // First restart interval (nullopt -> use Ganak's built-in default of
  // 20 000 conflicts).  Only meaningful when do_restart is true.
  std::optional<uint64_t> first_restart;

  // Enable cube-and-conquer restarts.  Ganak defaults to disabled (false);
  // enabling this can dramatically speed up hard instances.
  bool do_restart = false;

  // Maximum component cache size in MB.  Ganak's default is 2 500 MB.
  // Raise this on machines with ample RAM to improve cache hit rates.
  uint64_t maximum_cache_size_mb = 2500;

  // Polarity heuristic used when branching.
  // kCache is often the best choice for knowledge-compilation workloads.
  GanakPolarType polar_type = GanakPolarType::kStandard;

  // Keep recently-used clauses in the clause DB during reduction.
  // Ganak's own comment notes this is "quite a bit faster on lower
  // time cut-offs" but loses its edge beyond ~2 000 s.
  bool rdb_keep_used = false;

  // -------------------------------------------------------------------------
  // Tree-decomposition (TD) options
  // -------------------------------------------------------------------------

  // Run the tree-decomposition pre-pass.  Disabling it falls back to pure
  // VSADS, which is faster on very simple instances.
  bool do_td = true;

  // Variables in a component must be fewer than this to attempt TD.
  uint32_t td_var_limit = 150000;

  // Flowcutter weight upper bound for the TD heuristic.
  double td_max_weight = 60.0;

  // Flowcutter weight lower bound for the TD heuristic.
  double td_min_weight = 7.0;

  // Divisor applied to raw treewidth scores.
  double td_divider = 1e3;

  // Exponential multiplier applied to treewidth scores.
  double td_exp_mult = 1.1;

  // Number of flowcutter iterations (restarts inside the decomposer).
  int td_iters = 900;
};

// ---------------------------------------------------------------------------
// ArjunOptions
// ---------------------------------------------------------------------------

struct ArjunOptions {
  // Verbosity (0 = silent).
  int verb = 0;

  // Run the Arjun minimisation pass at all.
  bool do_arjun = true;

  // Exploit detected gates during minimisation.
  bool arjun_gates = true;

  // Run a backbone computation before the main minimisation pass.
  bool do_pre_backbone = false;

  // Use probe-based techniques.
  bool do_probe_based = true;

  // Simplification level passed to CryptoMiniSat inside Arjun (0-3).
  int arjun_simp_level = 2;

  // Maximum conflict budget for the backward-minimisation oracle.
  int arjun_backw_maxc = 20000;

  // Number of binary clauses the oracle may add.
  int arjun_oracle_find_bins = 6;

  // Global multiplier for CryptoMiniSat conflict limits (< 0 = default).
  double arjun_cms_glob_mult = -1.0;

  // Maximum conflicts used when extending the independent support.
  int arjun_extend_max_confl = 1000;

  // Use CCNR during extension.
  bool arjun_extend_ccnr = false;

  // Apply autarky reasoning.
  bool arjun_autarkies = false;

  // Run the PUURA elimination-to-file post-processing step.
  bool do_puura = true;

  // Minimum number of sampling variables before PUURA is attempted.
  uint32_t arjun_further_min_cutoff = 10;

  // Number of threads for Arjun (1 = single-threaded).
  int num_threads = 1;

  // Strip optional independent variables.
  bool strip_opt_indep = false;

  // Treat the full variable set as independent (sets all_indep in Arjun).
  bool all_indep = false;
};

// ---------------------------------------------------------------------------
// D4Options
// ---------------------------------------------------------------------------

enum class D4PreprocMethod {
  kEquiv,
  kBackbone,
  kVivi,
  kOccElim,
  kComb,
  kBasic,
};

enum class D4Solver {
  kGlucose,
  kMinisat,
};

struct D4Options {
  // Pre-processing
  D4PreprocMethod preproc_method  = D4PreprocMethod::kEquiv;
  int preproc_nb_iter = 5;
  int preproc_timeout = 60;

  // Branching heuristic decay frequency
  int freq_decay = 2048;

  // SAT solver back-end
  D4Solver solver = D4Solver::kGlucose;

  // Component cache sizes (bytes)
  unsigned long cache_first_page = 1UL << 32;  // NOLINT
  unsigned long cache_extra_page = 1UL << 29;  // NOLINT
};

}  // namespace kmpyl

#endif  // INCLUDE_KOMPYLE_OPTIONS_H_
