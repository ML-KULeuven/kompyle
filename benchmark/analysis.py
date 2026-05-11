# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2

from __future__ import annotations

import json
from time    import perf_counter
from typing  import Any

import torch
import torch.profiler

from util import (
    _silence_fd,
    _restore_fd,
    numpy_weights,
    compile_result_path,
    experiment_result_path
)


# ---------------------------------------------------------------------------
# STRUCTURE
# ---------------------------------------------------------------------------

def _is_relay_layer(ix_in: torch.Tensor, ix_out: torch.Tensor) -> bool:
    """
    A layer is a relay (dummy passthrough) iff every output node has exactly
    one incoming edge, i.e. the scatter is a simple gather, not a real
    reduction.

    A relay layer has len(edges) == number of unique output indices.
    """
    n_edges   = ix_in.shape[0]
    n_outputs = int(ix_out[-1].item()) + 1
    return n_edges == n_outputs


def analyze_circuit_module(circuit_module) -> dict[str, Any]:
    """
    Walk all layers and return a dict with:

      relay_layers        : count of layers where every node has 1 child
      total_layers        : total layer count
      relay_fraction      : relay_layers / total_layers
      dummy_edges         : edges that belong to relay layers
      real_edges          : edges that perform genuine reductions
      dummy_edge_fraction : dummy_edges / total_edges
      index_bytes_total   : bytes in ix_in + ix_out buffers across all layers
      index_bytes_dummy   : bytes consumed by relay-layer index buffers
      index_bytes_real    : bytes consumed by non-relay-layer index buffers
      per_layer           : list of per-layer stats
    """
    relay_layers = 0
    dummy_edges  = 0
    real_edges   = 0
    bytes_dummy  = 0
    bytes_real   = 0
    per_layer    = []

    for i, layer in enumerate(circuit_module.layers):
        ix_in    = layer.ix_in
        ix_out   = layer.ix_out
        n_edges  = ix_in.shape[0]
        relay    = _is_relay_layer(ix_in, ix_out)
        # each index tensor is int64 = 8 bytes
        buf_bytes = (ix_in.numel() + ix_out.numel()) * 8

        if relay:
            relay_layers += 1
            dummy_edges  += n_edges
            bytes_dummy  += buf_bytes
        else:
            real_edges   += n_edges
            bytes_real   += buf_bytes

        per_layer.append({
            "layer_idx": i,
            "n_edges":   n_edges,
            "n_outputs": int(ix_out[-1].item()) + 1,
            "relay":     relay,
            "buf_bytes": buf_bytes,
        })

    total_layers = len(circuit_module.layers)
    total_edges  = dummy_edges + real_edges
    total_bytes  = bytes_dummy + bytes_real

    return {
        "relay_layers":        relay_layers,
        "total_layers":        total_layers,
        "relay_fraction":      relay_layers / total_layers if total_layers else 0.0,
        "dummy_edges":         dummy_edges,
        "real_edges":          real_edges,
        "total_edges":         total_edges,
        "dummy_edge_fraction": dummy_edges / total_edges if total_edges else 0.0,
        "index_bytes_total":   total_bytes,
        "index_bytes_dummy":   bytes_dummy,
        "index_bytes_real":    bytes_real,
        "per_layer":           per_layer,
    }


# ---------------------------------------------------------------------------
# PROFILE
# ---------------------------------------------------------------------------

def _mk_weights(nb_vars, semiring, device, batch_size):
    w, nw = numpy_weights(nb_vars, semiring, batch_size)
    return torch.as_tensor(w).to(device), torch.as_tensor(nw).to(device)


def profiled_forward(
    circuit_module,
    nb_vars:    int,
    semiring:   str,
    device:     str,
    nb_repeats: int = 20,
    batch_size: int = 32,
) -> dict[str, Any]:
    """
    Run the forward pass under torch.profiler and return timing + op stats.

    Two warmup passes are run before recording.

    Returns a dict with:
      wall_times_s      : wall-clock seconds per forward pass
      wall_mean_s
      wall_median_s
      total_self_cpu_us : total self-CPU microseconds for one profiled pass
      scatter_cpu_us    : self-CPU µs in scatter_reduce ops specifically
      scatter_cpu_frac
      mem_alloc_bytes
      top_ops           : top-10 ops by self CPU time
    """
    module = circuit_module
    if batch_size is not None:
        module = torch.vmap(module)

    # warmup
    with torch.no_grad():
        for _ in range(3):
            w, nw = _mk_weights(nb_vars, semiring, device, batch_size)
            module(w, nw)

    # wall-time loop (no profiler overhead)
    wall_times: list[float] = []
    with torch.no_grad():
        for _ in range(nb_repeats):
            w, nw = _mk_weights(nb_vars, semiring, device, batch_size)
            t0 = perf_counter()
            module(w, nw)
            if device == "cuda":
                torch.cuda.synchronize()
            wall_times.append(perf_counter() - t0)

    # single profiler pass
    activities = [torch.profiler.ProfilerActivity.CPU]
    if device == "cuda":
        activities.append(torch.profiler.ProfilerActivity.CUDA)

    w, nw = _mk_weights(nb_vars, semiring, device, batch_size)
    with torch.profiler.profile(
        activities=activities,
        record_shapes=True,
        profile_memory=True,
        with_stack=False,
    ) as prof:
        with torch.no_grad():
            module(w, nw)

    key_avgs = prof.key_averages()

    scatter_cpu_us  = sum(e.self_cpu_time_total for e in key_avgs if "scatter" in e.key.lower())
    total_cpu_us    = sum(e.self_cpu_time_total for e in key_avgs)
    total_mem_alloc = sum(e.self_cpu_memory_usage for e in key_avgs if e.self_cpu_memory_usage > 0)

    top_ops = sorted(key_avgs, key=lambda e: e.self_cpu_time_total, reverse=True)[:10]
    top_ops_serialisable = [
        {
            "op":             e.key,
            "self_cpu_us":    e.self_cpu_time_total,
            "cpu_us":         e.cpu_time_total,
            "self_mem_bytes": e.self_cpu_memory_usage,
            "count":          e.count,
        }
        for e in top_ops
    ]

    return {
        "wall_times_s":      wall_times,
        "wall_mean_s":       sum(wall_times) / len(wall_times),
        "wall_median_s":     float(sorted(wall_times)[len(wall_times) // 2]),
        "total_self_cpu_us": total_cpu_us,
        "scatter_cpu_us":    scatter_cpu_us,
        "scatter_cpu_frac":  scatter_cpu_us / total_cpu_us if total_cpu_us else 0.0,
        "mem_alloc_bytes":   total_mem_alloc,
        "top_ops":           top_ops_serialisable,
    }


def run_one_experiment(
    exp_id:     int,
    nb_vars:    int,
    ratio:      float,
    seed:       int,
    backend:    str,
    semiring:   str,
    dev:        str,
    collapse:   bool = False,
    merge:      bool = False,
    nb_repeats: int = 20,
    batch_size: int = 32,
) -> int:
    """
    Run the dummy-node overhead experiment for one parameter set.

    Returns 0 on success, 1 on skip or error.
    """
    import kompyle as p
    from pysdd.sdd import SddManager

    # gate on a successful compile result
    cp = compile_result_path(exp_id, nb_vars, ratio, seed, backend)
    if not cp.exists():
        print(f"[skip] no compile result: {cp}")
        return 1

    cr = json.loads(cp.read_text())
    if cr.get("compile_s") is None:
        print(f"[skip] compile timed-out or errored: {cp}")
        return 1

    out = experiment_result_path(exp_id, nb_vars, ratio, seed, backend, semiring, dev)
    if out.exists():
        print(f"[skip] {out}")
        return 0

    # recompile
    cnf     = f"instances/v{nb_vars}_r{ratio:.1f}_s{seed}.cnf"
    circuit = p.Circuit()
    devnull, old_out, old_err = _silence_fd()

    try:
        if backend == "ganak":
            root = p.compile_from_cnf_using_ganak(circuit, cnf, arjun_options=None)
        elif backend == "ganak_arjun":
            ao = p.ArjunOptions()
            root = p.compile_from_cnf_using_ganak(circuit, cnf, arjun_options=ao)
        elif backend == "d4v2":
            root = p.compile_from_cnf_using_d4v2(circuit, cnf)
        elif backend == "sdd":
            mgr, sdd = SddManager.from_cnf_file(cnf.encode(), vtree_type=b"balanced")
            root = p.compile_from_sdd(circuit, sdd)
        else:
            raise ValueError(f"Unknown backend: {backend}")
    except Exception as e:
        _restore_fd(devnull, old_out, old_err)
        print(f"ERROR  recompile failed: {e}")
        return 1

    _restore_fd(devnull, old_out, old_err)
    assert root is not None
    circuit.set_root(root)

    module = circuit.to_torch_module(semiring, collapse=collapse, merge=merge)
    module.to(dev)

    # 1. structural analysis
    structural = analyze_circuit_module(module)

    # # 2. profiled timing
    # timing = profiled_forward(
    #     module, nb_vars, semiring, dev,
    #     nb_repeats=nb_repeats,
    #     batch_size=batch_size,
    # )

    result = {
        "nb_vars":       nb_vars,
        "ratio":         ratio,
        "seed":          seed,
        "backend":       backend,
        "semiring":      semiring,
        "device":        dev,
        "circuit_nodes": cr["circuit_nodes"],
        "circuit_edges": cr.get("circuit_edges"),
        "circuit_depth": cr.get("circuit_depth"),
        "structural":    structural,
        # "timing":        timing,
    }

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2))

    print(
        f"OK  {backend:8s}  {semiring:4s}"
        f"  v={nb_vars:3d}  r={ratio:.1f}  s={seed}"
        f"  relay={structural['relay_fraction']:.1%}"
        f"  dummy_edges={structural['dummy_edge_fraction']:.1%}"
        # f"  wall={timing['wall_median_s']*1e3:.2f}ms"
        # f"  scatter={timing['scatter_cpu_frac']:.1%}"
    )
    return 0

def run_one_experiment_cnf(
    exp_id:     int,
    cnf_path:   str,
    backend:    str,
    semiring:   str,
    dev:        str,
    collapse:   bool = False,
    merge:      bool = False,
    nb_repeats: int  = 20,
    batch_size: int  = 32,
) -> int:
    """
    Run the dummy-node overhead experiment for a real (non-synthetic) CNF.
    Result paths are keyed by the CNF file stem.
    Returns 0 on success, 1 on skip or error.
    """
    import kompyle as p
    from pathlib import Path
    from pysdd.sdd import SddManager
    from util import (
        compile_result_path_cnf,
        experiment_result_path_cnf,
        read_nb_vars_from_cnf,
    )

    stem = Path(cnf_path).stem

    cp = compile_result_path_cnf(exp_id, stem, backend)
    if not cp.exists():
        print(f"[skip] no compile result: {cp}")
        return 1

    cr = json.loads(cp.read_text())
    if cr.get("compile_s") is None:
        print(f"[skip] compile timed-out or errored: {cp}")
        return 1

    out = experiment_result_path_cnf(exp_id, stem, backend, semiring, dev)
    if out.exists():
        print(f"[skip] {out}")
        return 0

    nb_vars = read_nb_vars_from_cnf(cnf_path)

    circuit = p.Circuit()
    devnull, old_out, old_err = _silence_fd()

    try:
        if backend == "ganak":
            root = p.compile_from_cnf_using_ganak(circuit, cnf_path, arjun_options=None)
        elif backend == "ganak_arjun":
            ao = p.ArjunOptions()
            root = p.compile_from_cnf_using_ganak(circuit, cnf_path, arjun_options=ao)
        elif backend == "d4v2":
            root = p.compile_from_cnf_using_d4v2(circuit, cnf_path)
        elif backend == "sdd":
            mgr, sdd = SddManager.from_cnf_file(cnf_path.encode(), vtree_type=b"balanced")
            root = p.compile_from_sdd(circuit, sdd)
        else:
            raise ValueError(f"Unknown backend: {backend}")
    except Exception as e:
        _restore_fd(devnull, old_out, old_err)
        print(f"ERROR  recompile failed: {e}")
        return 1

    _restore_fd(devnull, old_out, old_err)
    assert root is not None
    circuit.set_root(root)

    module = circuit.to_torch_module(semiring, collapse=collapse, merge=merge)
    module.to(dev)

    structural = analyze_circuit_module(module)

    result = {
        "cnf":           cnf_path,
        "stem":          stem,
        "backend":       backend,
        "semiring":      semiring,
        "device":        dev,
        "nb_vars":       nb_vars,
        "circuit_nodes": cr["circuit_nodes"],
        "circuit_edges": cr.get("circuit_edges"),
        "circuit_depth": cr.get("circuit_depth"),
        "structural":    structural,
    }

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2))

    print(
        f"OK  {backend:8s}  {semiring:4s}"
        f"  cnf={Path(cnf_path).name:40s}"
        f"  relay={structural['relay_fraction']:.1%}"
        f"  dummy_edges={structural['dummy_edge_fraction']:.1%}"
    )
    return 0
