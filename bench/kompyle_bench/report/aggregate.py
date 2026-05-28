# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2
"""Turn raw result rows into chart-ready series."""

from __future__ import annotations

import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any

from kompyle_bench.report.load import (
    load_meta,
    load_compile,
    load_count,
    load_experiment,
    load_infer,
)


def _mean(vals: list) -> float | None:
    v = [x for x in vals if x is not None]
    return statistics.mean(v) if v else None


def _cumsum_sorted(vals: list[float]) -> list[float]:
    out: list[float] = []
    acc = 0.0
    for v in sorted(vals):
        acc += v
        out.append(round(acc, 6))
    return out

# -----------------------------------------------------------------
# aggregators
# -----------------------------------------------------------------

def _combined_cactus(
    compile_rows: list[dict],
    count_rows:   list[dict],
    n_instances:  int | None = None,
) -> dict:
    def cumsum_s(rows: list[dict], time_key: str) -> tuple[list[float], int, int, int]:
        times = sorted(
            r[time_key]
            for r in rows
            if r.get(time_key) is not None and not r.get("timed_out")
        )
        cs: list[float] = []
        acc = 0.0
        for v in times:
            acc += v
            cs.append(round(acc, 6))
        n_solved = len(times)
        n_failed = (n_instances or len(rows)) - n_solved
        return cs, n_solved, n_failed, len(rows)

    compile_backends = sorted({r["backend"] for r in compile_rows})
    count_backends   = sorted({r["backend"] for r in count_rows})

    compile_series = {}
    for b in compile_backends:
        rows_b = [r for r in compile_rows if r["backend"] == b]
        cumsum, n_solved, n_failed, n_total = cumsum_s(rows_b, "compile_s")
        compile_series[b] = {
            "backend":  b,
            "cumsum":   cumsum,
            "n_solved": n_solved,
            "n_failed": n_failed,
            "n_total":  n_total,
        }

    count_series = {}
    for b in count_backends:
        rows_b = [r for r in count_rows if r["backend"] == b]
        cumsum, n_solved, n_failed, n_total = cumsum_s(rows_b, "count_s")
        count_series[b] = {
            "backend":  b,
            "cumsum":   cumsum,
            "n_solved": n_solved,
            "n_failed": n_failed,
            "n_total":  n_total,
        }

    return {
        "compile_backends": compile_backends,
        "count_backends":   count_backends,
        "compile_series":   compile_series,
        "count_series":     count_series,
    }


def _infer_cactus(
    infer_rows: list[dict],
    backends: list[str],
    semirings: list[str],
    devices: list[str],
) -> dict:
    fwd: dict[tuple, list] = defaultdict(list)
    bwd: dict[tuple, list] = defaultdict(list)
    for r in infer_rows:
        key = (r["backend"], r["semiring"], r["device"])
        if r["forward_mean_ms"] is not None:
            fwd[key].append(r["forward_mean_ms"] / 1000)
        if r["backward_mean_ms"] is not None:
            bwd[key].append(r["backward_mean_ms"] / 1000)

    series = {}
    for b in backends:
        for sr in semirings:
            for dev in devices:
                key = (b, sr, dev)
                if not fwd.get(key):
                    continue
                series[f"{b}/{sr}/{dev}"] = {
                    "backend":         b,
                    "semiring":        sr,
                    "device":          dev,
                    "n":               len(fwd[key]),
                    "forward_cumsum":  _cumsum_sorted(fwd[key]),
                    "backward_cumsum": _cumsum_sorted(bwd[key]) if bwd.get(key) else [],
                }
    return {"semirings": semirings, "devices": devices, "series": series}


def _exp_chart(
    exp_rows: list[dict],
    backends: list[str],
    semirings: list[str],
    devices: list[str],
) -> dict:
    e_by: dict[tuple, dict[str, list]] = defaultdict(lambda: defaultdict(list))
    fields = ("relay_fraction",)
    for r in exp_rows:
        key = (r["backend"], r["semiring"], r["device"])
        for field in fields:
            if r.get(field) is not None:
                e_by[key][field].append(r[field])

    chart: dict[str, Any] = {"keys": []}
    for field in fields:
        chart[field] = []
    for b in backends:
        for sr in semirings:
            for dev in devices:
                key = (b, sr, dev)
                if key not in e_by:
                    continue
                chart["keys"].append(f"{b}<br>{sr}/{dev}")
                for field in fields:
                    chart[field].append(_mean(e_by[key][field]))
    return chart


def _instance_profile(infer_rows: list[dict], backends: list[str]) -> dict:
    nodes: dict[str, list] = defaultdict(list)
    sparsity: dict[str, list] = defaultdict(list)
    seen: set = set()
    for r in infer_rows:
        ident = (r["backend"], r.get("nb_vars"), r.get("ratio"),
                 r.get("seed"), r.get("stem"))
        if ident in seen:
            continue
        seen.add(ident)
        if r["circuit_nodes"] is not None:
            nodes[r["backend"]].append(r["circuit_nodes"])
        if r.get("sparsity") is not None:
            sparsity[r["backend"]].append(r["sparsity"])

    return {
        "backends":             backends,
        "nodes_by_backend":     {b: sorted(nodes[b])                    for b in backends if b in nodes},
        "sparsity_by_backend":  {b: sorted(sparsity[b], reverse=True)   for b in backends if b in sparsity},
    }


def _ident_key(r: dict) -> tuple:
    """Canonical key for an instance, regardless of synthetic vs real."""
    return (r.get("nb_vars"), r.get("ratio"), r.get("seed"), r.get("stem"))


def _compile_name_for(count_backend: str) -> str | None:
    suffix = "_count"
    if count_backend.endswith(suffix):
        return count_backend[: -len(suffix)]
    return None


def _solver_overhead(
    compile_rows: list[dict],
    count_rows:   list[dict],
) -> dict:
    """Per-backend solver-overhead aggregation."""
    by_compile: dict[tuple, dict] = {
        (r["backend"], _ident_key(r)): r
        for r in compile_rows
        if r.get("compile_s") is not None and not r.get("timed_out")
    }
    by_count: dict[tuple, dict] = {
        (r["backend"], _ident_key(r)): r
        for r in count_rows
        if r.get("count_s") is not None and not r.get("timed_out")
    }

    count_backends = sorted({r["backend"] for r in count_rows})
    pairs: dict[str, dict] = {}

    for cb in count_backends:
        compile_backend = _compile_name_for(cb)
        if compile_backend is None:
            continue
        joined: list[tuple[dict, dict]] = []
        for (b, ident), c_row in by_count.items():
            if b != cb:
                continue
            cc = by_compile.get((compile_backend, ident))
            if cc is None:
                continue
            joined.append((cc, c_row))

        if not joined:
            continue

        compile_s  = sorted(cc["compile_s"] for cc, _ in joined)
        count_s    = sorted(c["count_s"] for _, c  in joined)
        overhead_s = sorted((cc["compile_s"] - c["count_s"]) for cc, c in joined)

        ratios     = sorted(
            (cc["compile_s"] / c["count_s"])
            for cc, c in joined
            if c["count_s"] > 0
        )

        def _cumsum(xs: list[float]) -> list[float]:
            out: list[float] = []
            acc = 0.0
            for v in xs:
                acc += v
                out.append(round(acc, 6))
            return out

        pairs[cb] = {
            "count_backend":   cb,
            "compile_backend": compile_backend,
            "n_pairs":         len(joined),
            "count_cumsum":    _cumsum(count_s),
            "compile_cumsum":  _cumsum(compile_s),
            "overhead_s":      [round(v, 6) for v in overhead_s],
            "ratios":          [round(v, 3)  for v in ratios],
        }

    return {"pairs": pairs}


# -----------------------------------------------------------------
# Top-level
# -----------------------------------------------------------------

def aggregate(benchmark_dir: Path, exp_name: str) -> dict[str, Any]:
    """Build the full chart-data payload for one experiment."""
    meta         = load_meta(benchmark_dir, exp_name)
    compile_rows = load_compile(benchmark_dir, exp_name)
    count_rows   = load_count(benchmark_dir, exp_name)
    infer_rows   = load_infer(benchmark_dir, exp_name)
    exp_rows     = load_experiment(benchmark_dir, exp_name)
 
    backends  = sorted({r["backend"]  for r in compile_rows})
    semirings = sorted({r["semiring"] for r in infer_rows})
    devices   = sorted({r["device"]   for r in infer_rows})

    n_instaces = meta.get("n_instances")
    return {
        "exp_name":         exp_name,
        "n_compile":        len(compile_rows),
        "n_count":          len(count_rows),
        "n_infer":          len(infer_rows),
        "n_experiment":     len(exp_rows),
        "infer_cactus":     _infer_cactus(infer_rows, backends, semirings, devices),
        "exp_chart":        _exp_chart(exp_rows, backends, semirings, devices),
        "instance_profile": _instance_profile(infer_rows, backends),
        "solver_overhead":  _solver_overhead(compile_rows, count_rows),
        "combined_cactus":  _combined_cactus(compile_rows, count_rows, n_instaces),
        "meta":             meta,
    }
