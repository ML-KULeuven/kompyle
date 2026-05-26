# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2
"""Turn raw result rows into chart-ready series."""

from __future__ import annotations

import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any

from kompyle_bench.report.load import (
    load_compile,
    load_count,
    load_experiment,
    load_infer,
)


def _compile_name_for(count_backend: str) -> str | None:
    suffix = "_count"
    if count_backend.endswith(suffix):
        return count_backend[: -len(suffix)]
    return None


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

def _compile_cactus(compile_rows: list[dict], backends: list[str]) -> dict:
    series = {}
    for b in backends:
        rows_b = [r for r in compile_rows if r["backend"] == b]
        times = sorted(
            r["compile_s"] * 1000
            for r in rows_b
            if r["compile_s"] is not None and not r.get("timed_out")
        )
        cumsums: list[float] = []
        acc = 0.0
        for v in times:
            acc += v
            cumsums.append(round(acc, 3))
        series[b] = {
            "backend":   b,
            "n_solved":  len(times),
            "n_timeout": sum(1 for r in rows_b if r.get("timed_out")),
            "n_total":   len(rows_b),
            "cumsum":    cumsums,
        }
    return {"backends": backends, "series": series}


def _combined_cactus(
    compile_rows: list[dict],
    count_rows:   list[dict],
) -> dict:
    """All compile + all count backends, side by side, on one cactus.

    Two series per timing variant. Compile series carry ``compile_s``;
    count series carry ``count_s``. Each is independently sorted (the
    usual cactus, no joining). The dashboard renders compile as a
    solid line and count as a dotted line, with the family inferred
    from the backend name (e.g. ``ganak`` and ``ganak_count`` share a
    family so they share a color).

    Unlike ``_solver_overhead`` this doesn't require the two stages to
    cover the same instances — useful for counters that have no
    matching compile backend, like ``isymganak_count``.
    """
    def cumsum_ms(rows: list[dict], time_key: str) -> tuple[list[float], int, int, int]:
        times = sorted(
            r[time_key] * 1000
            for r in rows
            if r.get(time_key) is not None and not r.get("timed_out")
        )
        cs: list[float] = []
        acc = 0.0
        for v in times:
            acc += v
            cs.append(round(acc, 3))
        n_timeout = sum(1 for r in rows if r.get("timed_out"))
        return cs, len(times), n_timeout, len(rows)

    compile_backends = sorted({r["backend"] for r in compile_rows})
    count_backends   = sorted({r["backend"] for r in count_rows})

    compile_series = {}
    for b in compile_backends:
        rows_b = [r for r in compile_rows if r["backend"] == b]
        cumsum, n_solved, n_timeout, n_total = cumsum_ms(rows_b, "compile_s")
        compile_series[b] = {
            "backend":   b,
            "cumsum":    cumsum,
            "n_solved":  n_solved,
            "n_timeout": n_timeout,
            "n_total":   n_total,
        }

    count_series = {}
    for b in count_backends:
        rows_b = [r for r in count_rows if r["backend"] == b]
        cumsum, n_solved, n_timeout, n_total = cumsum_ms(rows_b, "count_s")
        count_series[b] = {
            "backend":   b,
            "cumsum":    cumsum,
            "n_solved":  n_solved,
            "n_timeout": n_timeout,
            "n_total":   n_total,
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
            fwd[key].append(r["forward_mean_ms"])
        if r["backward_mean_ms"] is not None:
            bwd[key].append(r["backward_mean_ms"])

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


def _solver_overhead(
    compile_rows: list[dict],
    count_rows:   list[dict],
) -> dict:
    """Per-backend solver-overhead aggregation.

    For each ``(compile_backend, count_backend)`` pair we join
    on instance identity and report

    * ``count_cumsum``    cactus of count-only times (sorted)
    * ``compile_cumsum``  cactus of compile times on the *same set*
                          of instances (sorted, may include instances
                          that count solved but compile didn't and
                          vice versa, those are dropped from the pair)
    * ``overhead_ms``     per-instance ``compile_s − count_s`` in ms,
                          sorted ascending. This is the headline chart:
                          it shows how much of the compile time is
                          circuit construction.
    * ``ratios``          per-instance ``compile_s / count_s``, sorted.
    """
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

        compile_ms = sorted(cc["compile_s"] * 1000 for cc, _ in joined)
        count_ms   = sorted(c["count_s"]   * 1000 for _, c  in joined)
        overhead   = sorted((cc["compile_s"] - c["count_s"]) * 1000 for cc, c in joined)
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
                out.append(round(acc, 3))
            return out

        pairs[cb] = {
            "count_backend":   cb,
            "compile_backend": compile_backend,
            "n_pairs":         len(joined),
            "count_cumsum":    _cumsum(count_ms),
            "compile_cumsum":  _cumsum(compile_ms),
            "overhead_ms":     [round(v, 3) for v in overhead],
            "ratios":          [round(v, 3) for v in ratios],
        }

    return {"pairs": pairs}


# -----------------------------------------------------------------
# Top-level
# -----------------------------------------------------------------

def aggregate(benchmark_dir: Path, exp_id: int) -> dict[str, Any]:
    """Build the full chart-data payload for one experiment."""
    compile_rows = load_compile(benchmark_dir, exp_id)
    count_rows   = load_count(benchmark_dir, exp_id)
    infer_rows   = load_infer(benchmark_dir, exp_id)
    exp_rows     = load_experiment(benchmark_dir, exp_id)

    backends  = sorted({r["backend"]  for r in compile_rows})
    semirings = sorted({r["semiring"] for r in infer_rows})
    devices   = sorted({r["device"]   for r in infer_rows})

    return {
        "exp_id":           exp_id,
        "n_compile":        len(compile_rows),
        "n_count":          len(count_rows),
        "n_infer":          len(infer_rows),
        "n_experiment":     len(exp_rows),
        "compile_cactus":   _compile_cactus(compile_rows, backends),
        "infer_cactus":     _infer_cactus(infer_rows, backends, semirings, devices),
        "exp_chart":        _exp_chart(exp_rows, backends, semirings, devices),
        "instance_profile": _instance_profile(infer_rows, backends),
        "solver_overhead":  _solver_overhead(compile_rows, count_rows),
        "combined_cactus":  _combined_cactus(compile_rows, count_rows),
    }
