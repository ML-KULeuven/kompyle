# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2
"""Read experiment result JSON files into row dicts.

The directory layout is::

    exps/exp<NNNN>/results/
        compile/<backend>/<key>.json
        infer/<backend>_<semiring>_<device>/<key>.json
        experiment/dummy_overhead/<backend>_<semiring>_<device>/<key>.json

``<key>`` is either a synthetic identifier ``vN_rR_sS`` or the stem of a
real CNF filename. Both flavours land in the same tree.
"""

from __future__ import annotations

import json
import re
import statistics
from pathlib import Path


def list_exp_ids(benchmark_dir: Path) -> list[int]:
    ids = []
    for p in benchmark_dir.glob("exps/exp*"):
        m = re.match(r"exp(\d+)$", p.name)
        if m:
            ids.append(int(m.group(1)))
    return sorted(ids)


def latest_exp_id(benchmark_dir: Path) -> int | None:
    ids = list_exp_ids(benchmark_dir)
    return max(ids) if ids else None


def exp_root(benchmark_dir: Path, exp_id: int) -> Path:
    return benchmark_dir / f"exps/exp{exp_id:04d}"


# -----------------------------------------------------------------
# parsing
# -----------------------------------------------------------------

_SYNTH_RE = re.compile(r"v(\d+)_r([\d.]+)_s(\d+)$")


def parse_key(stem: str) -> dict:
    """Parse a JSON filename stem into identifying fields.

    Synthetic stems (``v10_r3.0_s2``) yield ``{nb_vars, ratio, seed}``;
    everything else is treated as a real instance and yields ``{stem}``.
    """
    m = _SYNTH_RE.match(stem)
    if m:
        return {
            "nb_vars": int(m.group(1)),
            "ratio":   float(m.group(2)),
            "seed":    int(m.group(3)),
            "stem":    stem,
        }
    return {"stem": stem}


def parse_infer_dir(dirname: str) -> tuple[str, str, str]:
    """Parse ``'ganak_arjun_real_cpu'`` -> ``('ganak_arjun', 'real', 'cpu')``."""
    parts = dirname.split("_")
    device = parts[-1]
    assert device in ("cuda", "cpu"), f"unexpected device in dir: {dirname}"
    semiring = parts[-2]
    assert semiring in ("real", "log"), f"unexpected semiring in dir: {dirname}"
    backend = "_".join(parts[:-2])
    return backend, semiring, device

# -----------------------------------------------------------------
# Loaders
# -----------------------------------------------------------------

def load_compile(benchmark_dir: Path, exp_id: int) -> list[dict]:
    rows: list[dict] = []
    base = exp_root(benchmark_dir, exp_id) / "results" / "compile"
    if not base.exists():
        return rows
    for f in base.rglob("*.json"):
        backend = f.parent.name
        ident = parse_key(f.stem)
        d = json.loads(f.read_text())
        rows.append({
            "exp_id":        exp_id,
            "backend":       backend,
            **ident,
            "compile_s":     d.get("compile_s"),
            "circuit_nodes": d.get("circuit_nodes"),
            "circuit_edges": d.get("circuit_edges"),
            "circuit_depth": d.get("circuit_depth"),
            "timed_out":     d.get("timed_out", False),
            "error":         d.get("error"),
        })
    return rows


def load_count(benchmark_dir: Path, exp_id: int) -> list[dict]:
    """Load count-stage results. Mirror of `load_compile`."""
    rows: list[dict] = []
    base = exp_root(benchmark_dir, exp_id) / "results" / "count"
    if not base.exists():
        return rows
    for f in base.rglob("*.json"):
        backend = f.parent.name
        ident = parse_key(f.stem)
        d = json.loads(f.read_text())
        rows.append({
            "exp_id":      exp_id,
            "backend":     backend,
            **ident,
            "count_s":     d.get("count_s"),
            "model_count": d.get("model_count"),
            "timed_out":   d.get("timed_out", False),
            "error":       d.get("error"),
        })
    return rows


def _ms_stats(vals: list[float] | None) -> tuple[float | None, float | None]:
    """Return ``(mean_ms, median_ms)`` from a list of seconds, or ``(None, None)``."""
    if not vals:
        return None, None
    return statistics.mean(vals) * 1000, statistics.median(vals) * 1000


def load_infer(benchmark_dir: Path, exp_id: int) -> list[dict]:
    rows: list[dict] = []
    base = exp_root(benchmark_dir, exp_id) / "results" / "infer"
    if not base.exists():
        return rows
    for f in base.rglob("*.json"):
        backend, semiring, device = parse_infer_dir(f.parent.name)
        ident = parse_key(f.stem)
        d = json.loads(f.read_text())
        fwd_mean, fwd_med = _ms_stats(d.get("forward (warm)"))
        bwd_mean, _bwd_med = _ms_stats(d.get(" +backward (warm)"))
        rows.append({
            "exp_id":            exp_id,
            "backend":           backend,
            "semiring":          semiring,
            "device":            device,
            **ident,
            "circuit_nodes":     d.get("circuit_nodes"),
            "sparsity":          d.get("sparsity"),
            "forward_mean_ms":   fwd_mean,
            "forward_median_ms": fwd_med,
            "backward_mean_ms":  bwd_mean,
            "to_torch_s":        d.get("to_torch"),
            "jit_compile_s":     d.get("jit compile"),
        })
    return rows


def load_experiment(benchmark_dir: Path, exp_id: int) -> list[dict]:
    rows: list[dict] = []
    base = exp_root(benchmark_dir, exp_id) / "results" / "experiment" / "dummy_overhead"
    if not base.exists():
        return rows
    for f in base.rglob("*.json"):
        backend, semiring, device = parse_infer_dir(f.parent.name)
        ident = parse_key(f.stem)
        d = json.loads(f.read_text())
        s = d.get("structural", {})
        t = d.get("timing", {})

        rf = s.get("relay_fraction")
        if s.get("relay_layers") == 1 and s.get("total_layers") == 1:
            rf = 0

        rows.append({
            "exp_id":              exp_id,
            "backend":             backend,
            "semiring":            semiring,
            "device":              device,
            **ident,
            "relay_fraction":      rf,
            "dummy_edge_fraction": s.get("dummy_edge_fraction"),
            "relay_layers":        s.get("relay_layers"),
            "total_layers":        s.get("total_layers"),
            "dummy_edges":         s.get("dummy_edges"),
            "total_edges":         s.get("total_edges"),
            "scatter_cpu_frac":    t.get("scatter_cpu_frac"),
            "wall_mean_ms":        (t.get("wall_mean_s")   or 0) * 1000,
            "wall_median_ms":      (t.get("wall_median_s") or 0) * 1000,
        })
    return rows
