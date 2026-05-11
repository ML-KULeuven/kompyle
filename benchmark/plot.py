#!/usr/bin/env python3
# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2
"""
The live server re-reads all result JSON on every page refresh
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
from collections import defaultdict
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any


BENCHMARK_DIR = Path(__file__).parent

def _list_exp_ids() -> list[int]:
    ids = []
    for p in BENCHMARK_DIR.glob("exps/exp*"):
        m = re.match(r"exp(\d+)$", p.name)
        if m:
            ids.append(int(m.group(1)))
    return sorted(ids)


def _latest_exp_id() -> int | None:
    ids = _list_exp_ids()
    return max(ids) if ids else None


def _exp_root(exp_id: int) -> Path:
    return BENCHMARK_DIR / f"exps/exp{exp_id:04d}"


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def _parse_stem(stem: str) -> tuple[int, float, int]:
    """Parse 'v10_r3.0_s2' → (10, 3.0, 2)."""
    m = re.match(r"v(\d+)_r([\d.]+)_s(\d+)$", stem)
    if not m:
        raise ValueError(f"Unexpected filename stem: {stem!r}")
    return int(m.group(1)), float(m.group(2)), int(m.group(3))


def _parse_backend_semiring_device(dirname: str) -> tuple[str, str, str]:
    """Parse 'ganak_arjun_real_cpu' → ('ganak_arjun', 'real', 'cpu')."""
    parts = dirname.split("_")

    device   = parts[-1]    # cpu  | cuda
    assert(device in ("cuda", "cpu"))

    semiring = parts[-2]    # real | log
    assert(semiring in ("real", "log"))

    backend  = "_".join(parts[:-2])
    assert(backend in ("d4v2", "ganak_arjun", "ganak", "sdd"))

    return backend, semiring, device 


def load_compile(exp_id: int) -> list[dict]:
    rows = []
    base = _exp_root(exp_id) / "results" / "compile"
    if not base.exists():
        return rows
    for f in base.rglob("*.json"):
        backend = f.parent.name
        nb_vars, ratio, seed = _parse_stem(f.stem)
        d = json.loads(f.read_text())
        rows.append({
            "exp_id":        exp_id,
            "backend":       backend,
            "nb_vars":       nb_vars,
            "ratio":         ratio,
            "seed":          seed,
            "compile_s":     d.get("compile_s"),
            "circuit_nodes": d.get("circuit_nodes"),
            "circuit_edges": d.get("circuit_edges"),
            "circuit_depth": d.get("circuit_depth"),
            "timed_out":     d.get("timed_out", False),
            "error":         d.get("error"),
        })
    return rows


def load_infer(exp_id: int) -> list[dict]:
    rows = []
    base = _exp_root(exp_id) / "results" / "infer"
    if not base.exists():
        return rows
    for f in base.rglob("*.json"):
        backend, semiring, device = _parse_backend_semiring_device(f.parent.name)
        nb_vars, ratio, seed = _parse_stem(f.stem)
        d = json.loads(f.read_text())
        warm_fwd  = d.get("forward (warm)", [])
        warm_bwd  = d.get(" +backward (warm)", [])
        rows.append({
            "exp_id":            exp_id,
            "backend":           backend,
            "semiring":          semiring,
            "device":            device,
            "nb_vars":           nb_vars,
            "ratio":             ratio,
            "seed":              seed,
            "circuit_nodes":     d.get("circuit_nodes"),
            "sparsity":          d.get("sparsity"),
            "forward_mean_ms":   statistics.mean(warm_fwd)  * 1000 if warm_fwd  else None,
            "forward_median_ms": statistics.median(warm_fwd)* 1000 if warm_fwd  else None,
            "backward_mean_ms":  statistics.mean(warm_bwd)  * 1000 if warm_bwd  else None,
            "to_torch_s":        d.get("to_torch"),
            "jit_compile_s":     d.get("jit compile"),
        })
    return rows


def load_experiment(exp_id: int) -> list[dict]:
    """Load experiment results."""
    rows = []

    base = _exp_root(exp_id) / "results" / "experiment" / "dummy_overhead"
    assert(base.exists())

    seen: set[Path] = set()
    seen.add(base)
    for f in base.rglob("*.json"):
        backend, semiring, device = _parse_backend_semiring_device(f.parent.name)
        nb_vars, ratio, seed = _parse_stem(f.stem)
        d = json.loads(f.read_text())
        s = d.get("structural", {})
        t = d.get("timing", {})

        rf = s.get("relay_fraction")
        rl = s.get("relay_layers")
        tl = s.get("total_layers")
        if (rl == 1) and (tl == 1):
            rf = 0

        rows.append({
            "exp_id":               exp_id,
            "backend":              backend,
            "semiring":             semiring,
            "device":               device,
            "nb_vars":              nb_vars,
            "ratio":                ratio,
            "seed":                 seed,
            "relay_fraction":       rf,
            "dummy_edge_fraction":  s.get("dummy_edge_fraction"),
            "relay_layers":         rl,
            "total_layers":         tl,
            "dummy_edges":          s.get("dummy_edges"),
            "total_edges":          s.get("total_edges"),
            "scatter_cpu_frac":     t.get("scatter_cpu_frac"),
            "wall_mean_ms":         t.get("wall_mean_s",   0) * 1000,
            "wall_median_ms":       t.get("wall_median_s", 0) * 1000,
        })

    return rows


def _mean(vals: list) -> float | None:
    v = [x for x in vals if x is not None]
    return statistics.mean(v) if v else None


def aggregate(exp_id: int) -> dict[str, Any]:
    compile_rows  = load_compile(exp_id)
    infer_rows    = load_infer(exp_id)
    exp_rows      = load_experiment(exp_id)

    backends  = sorted({r["backend"]    for r in compile_rows})
    ratios    = sorted({r["ratio"]      for r in compile_rows})
    semirings = sorted({r["semiring"]   for r in infer_rows})
    devices   = sorted({r["device"]     for r in infer_rows})

    compile_cactus = {"backends": backends, "series": {}}
    for b in backends:
        rows_b = [r for r in compile_rows if r["backend"] == b]
        times = sorted(r["compile_s"] * 1000 for r in rows_b
                       if r["compile_s"] is not None and not r.get("timed_out"))
        n_total = len(rows_b)
        n_timeout = sum(1 for r in rows_b if r.get("timed_out"))
        cumsums, acc = [], 0.0
        for v in times:
            acc += v
            cumsums.append(round(acc, 3))
        compile_cactus["series"][b] = {
            "backend":   b,
            "n_solved":  len(times),
            "n_timeout": n_timeout,
            "n_total":   n_total,
            "cumsum":    cumsums,
        }

    infer_cactus_fwd = defaultdict(list)
    infer_cactus_bwd = defaultdict(list)
    for r in infer_rows:
        key = (r["backend"], r["semiring"], r["device"])
        if r["forward_mean_ms"] is not None:
            infer_cactus_fwd[key].append(r["forward_mean_ms"])
        if r["backward_mean_ms"] is not None:
            infer_cactus_bwd[key].append(r["backward_mean_ms"])

    def _cumsum_sorted(vals):
        s = sorted(vals)
        out, acc = [], 0.0
        for v in s:
            acc += v
            out.append(round(acc, 6))
        return out

    infer_cactus = {"semirings": semirings, "devices": devices, "series": {}}
    for b in backends:
        for sr in semirings:
            for dev in devices:
                key = (b, sr, dev)
                fwd = infer_cactus_fwd.get(key, [])
                bwd = infer_cactus_bwd.get(key, [])
                if not fwd:
                    continue
                infer_cactus["series"][f"{b}/{sr}/{dev}"] = {
                    "backend":  b,
                    "semiring": sr,
                    "device":   dev,
                    "n":        len(fwd),
                    "forward_cumsum":  _cumsum_sorted(fwd),
                    "backward_cumsum": _cumsum_sorted(bwd) if bwd else [],
                }

    e_by: dict[tuple, dict[str, list]] = defaultdict(lambda: defaultdict(list))
    for r in exp_rows:
        key = (r["backend"], r["semiring"], r["device"])
        for field in ("relay_fraction",
                      # "dummy_edge_fraction", "scatter_cpu_frac", "wall_median_ms"
                      ):
            if r.get(field) is not None:
                e_by[key][field].append(r[field])

    exp_chart = {
        "keys": [],
        "relay_fraction":      [],
        # "dummy_edge_fraction": [],
        # "scatter_cpu_frac":    [],
        # "wall_median_ms":      [],
    }
    for b in backends:
        for sr in semirings:
            for dev in devices:
                key = (b, sr, dev)
                if key not in e_by:
                    continue
                exp_chart["keys"].append(f"{b}<br>{sr}/{dev}")
                for field in ("relay_fraction",
                        # "dummy_edge_fraction", "scatter_cpu_frac", "wall_median_ms"
                              ):
                    exp_chart[field].append(_mean(e_by[key][field]))

    nodes_by_backend: dict[str, list] = defaultdict(list)
    sparsity_by_backend: dict[str, list] = defaultdict(list)
    seen_inst: set = set()
    for r in infer_rows:
        inst_key = (r["backend"], r["nb_vars"], r["ratio"], r["seed"])
        if inst_key not in seen_inst:
            if r["circuit_nodes"] is not None:
                nodes_by_backend[r["backend"]].append(r["circuit_nodes"])
            if r.get("sparsity") is not None:
                sparsity_by_backend[r["backend"]].append(r["sparsity"])
            seen_inst.add(inst_key)

    instance_profile = {
        "backends":           backends,
        "nodes_by_backend":   {b: sorted(nodes_by_backend[b])   for b in backends if b in nodes_by_backend},
        "sparsity_by_backend":{b: sorted(sparsity_by_backend[b], reverse=True) for b in backends if b in sparsity_by_backend},
    }

    return {
        "exp_id":           exp_id,
        "n_compile":        len(compile_rows),
        "n_infer":          len(infer_rows),
        "n_experiment":     len(exp_rows),
        "compile_cactus":   compile_cactus,
        "infer_cactus":     infer_cactus,
        "exp_chart":        exp_chart,
        "instance_profile": instance_profile,
    }


# ---------------------------------------------------------------------------
# HTML template
# ---------------------------------------------------------------------------

def _template() -> str:
    """Read index.html from the same directory as this script."""
    return (BENCHMARK_DIR / "index.html").read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------

def _make_handler(exp_id: int | None):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):  # pyright:ignore
            pass

        def _eid(self):
            from urllib.parse import urlparse, parse_qs
            qs = parse_qs(urlparse(self.path).query)
            if 'exp_id' in qs:
                return int(qs['exp_id'][0])
            return exp_id if exp_id is not None else _latest_exp_id()

        def _path(self):
            from urllib.parse import urlparse
            return urlparse(self.path).path

        def do_GET(self):
            path = self._path()
            if path in ("/", "/index.html"):
                body = _template().encode()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            elif path == "/api/experiments":
                ids = _list_exp_ids()
                body = json.dumps(ids).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()
                self.wfile.write(body)

            elif path == "/api/results":
                eid = self._eid()
                if eid is None:
                    self.send_response(404)
                    self.end_headers()
                    self.wfile.write(b"No experiment folders found")
                    return
                try:
                    data = aggregate(eid)
                    body = json.dumps(data).encode()
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Length", str(len(body)))
                    self.send_header("Cache-Control", "no-cache")
                    self.end_headers()
                    self.wfile.write(body)
                    print(f"  /api/results → exp{eid:04d}  "
                          f"({data['n_compile']} compile, "
                          f"{data['n_infer']} infer, "
                          f"{data['n_experiment']} experiment)")
                except Exception as exc:
                    body = str(exc).encode()
                    self.send_response(500)
                    self.send_header("Content-Type", "text/plain")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)

            else:
                self.send_response(404)
                self.end_headers()

    return Handler

def main():
    parser = argparse.ArgumentParser(
        description="Kompyle benchmark dashboard — live server or static export.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--serve", action="store_true",
                        help="Start live HTTP server (refresh page to pick up new results)")
    parser.add_argument("--port", type=int, default=8080, metavar="PORT")
    parser.add_argument("--exp-id", type=int, default=None, metavar="ID",
                        help="Experiment ID to visualise (default: latest)")
    parser.add_argument("--out", default="dashboard.html", metavar="PATH",
                        help="Output path for static export (default: dashboard.html)")
    args = parser.parse_args()

    if args.serve:
        handler = _make_handler(args.exp_id)
        server  = HTTPServer(("", args.port), handler)
        eid_desc = f"exp{args.exp_id:04d}" if args.exp_id else "latest exp (auto-detected on each request)"
        print(f"Serving at http://localhost:{args.port}  [{eid_desc}]")
        print("Refresh the browser page to pick up new results from ./sweep.sh")
        print("Ctrl-C to stop.\n")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")

if __name__ == "__main__":
    main()
