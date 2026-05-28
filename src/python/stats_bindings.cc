// Copyright (c) 2026 Ibrahim El Kaddouri
// Licensed under apachev2
//
// Python bindings for the per-operation stats globals used by the
// klay-overhead benchmark.

#include "nanobind/nanobind.h"
#include "nanobind/stl/string.h"  // IWYU pragma: keep

#include "python/bindings.h"
#include "ganak/field_stats.h"
#include "d4/d4_stats.h"

namespace kmpyl {

namespace nb = nanobind;

namespace {

nb::dict FillStats(const FieldStats& s) {
  nb::dict d;
  d["n_dup"]        = s.n_dup.load();
  d["ns_dup"]       = s.ns_dup.load();
  d["n_gen_dup"]    = s.n_gen_dup.load();
  d["ns_gen_dup"]   = s.ns_gen_dup.load();
  d["n_add"]        = s.n_add.load();
  d["ns_add"]       = s.ns_add.load();
  d["n_mul"]        = s.n_mul.load();
  d["ns_mul"]       = s.ns_mul.load();
  d["n_zero"]       = s.n_zero.load();
  d["ns_zero"]      = s.ns_zero.load();
  d["n_one"]        = s.n_one.load();
  d["ns_one"]       = s.ns_one.load();
  d["n_lit_field"]  = s.n_lit_field.load();
  d["ns_lit_field"] = s.ns_lit_field.load();
  return d;
}

nb::dict FillStats(const D4OpStats& s) {
  nb::dict d;
  d["n_top"]      = s.n_top.load();
  d["ns_top"]     = s.ns_top.load();
  d["n_bottom"]   = s.n_bottom.load();
  d["ns_bottom"]  = s.ns_bottom.load();
  d["n_branch"]   = s.n_branch.load();
  d["ns_branch"]  = s.ns_branch.load();
  d["n_add"]      = s.n_add.load();
  d["ns_add"]     = s.ns_add.load();
  d["n_mul"]      = s.n_mul.load();
  d["ns_mul"]     = s.ns_mul.load();
  d["n_lit_node"] = s.n_lit_node.load();
  d["ns_lit_node"] = s.ns_lit_node.load();
  d["n_taut"]     = s.n_taut.load();
  d["ns_taut"]    = s.ns_taut.load();
  return d;
}

}  // namespace

void InitStatsBindings(nb::module_& m) {
  m.def(
      "get_ganak_stats",
      []() -> nb::dict {
        nb::dict out;
        out["circuit"] = FillStats(g_gk_stats_circuit);
        out["count"]   = FillStats(g_gk_stats_count);
        return out;
      },
      "Snapshot the ganak per-Field-operation counters.\n\n"
      "Returns\n"
      "-------\n"
      "dict\n"
      "    ``{\"circuit\": {...}, \"count\": {...}}`` where each inner\n"
      "    dict maps every ``n_*`` (call count) and ``ns_*`` (total\n"
      "    nanoseconds) counter on ``FieldStats`` to its current\n"
      "    value.  Subtract ``count`` from ``circuit`` per key to get\n"
      "    the klay-related overhead.");

  m.def(
      "get_d4_stats",
      []() -> nb::dict {
        nb::dict out;
        out["circuit"] = FillStats(g_d4_stats_circuit);
        out["count"]     = FillStats(g_d4_stats_count);
        return out;
      },
      "Snapshot the d4v2 per-Operation counters.\n\n"
      "Returns\n"
      "-------\n"
      "dict\n"
      "    ``{\"circuit\": {...}, \"count\": {...}}`` where each inner\n"
      "    dict maps every ``n_*`` (call count) and ``ns_*`` (total\n"
      "    nanoseconds) counter on ``D4OpStats`` to its current\n"
      "    value.  Subtract ``count`` from ``circuit`` per key to get\n"
      "    the klay-related overhead.");

  m.def(
      "reset_ganak_stats",
      []() {
        g_gk_stats_circuit.reset();
        g_gk_stats_count.reset();
      },
      "Zero both ganak stats globals (circuit and count).");

  m.def(
      "reset_d4_stats",
      []() {
        g_d4_stats_circuit.reset();
        g_d4_stats_count.reset();
      },
      "Zero both d4 stats globals (circuit and count).");

  m.def(
      "reset_all_stats",
      []() {
        g_gk_stats_circuit.reset();
        g_gk_stats_count.reset();
        g_d4_stats_circuit.reset();
        g_d4_stats_count.reset();
      },
      "Zero all four stats globals.");
}

}  // namespace kmpyl
