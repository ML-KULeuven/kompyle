# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2
"""Experiment-stage runner"""

from __future__ import annotations

from kompyle_bench.analyze import analyze_circuit_module
from kompyle_bench.backends import compile_with
from kompyle_bench.instance import Instance
from kompyle_bench.io import silenced_fds
from kompyle_bench.paths import compile_result_path, experiment_result_path
from kompyle_bench.runners._common import (
    load_compile_result,
    skip_if_exists,
    write_json,
)


def run_experiment(
    *,
    exp_id:     int,
    instance:   Instance,
    backend:    str,
    semiring:   str,
    device:     str,
) -> int:
    """Structural-analysis run for one parameter combination.

    Returns 0 on success-or-skip, 1 on error.
    """
    cp = compile_result_path(exp_id, instance, backend)
    cr = load_compile_result(cp)
    if cr is None:
        return 0 if cp.exists() else 1

    out = experiment_result_path(exp_id, instance, backend, semiring, device)
    if skip_if_exists(out):
        return 0

    cnf = str(instance.cnf_path())
    try:
        with silenced_fds():
            compile_out = compile_with(backend, cnf)
    except Exception as e:
        print(f"ERROR  recompile failed: {e}")
        return 1

    module = compile_out.circuit.to_torch_module(semiring)  # pyright:ignore
    module.to(device)
    structural = analyze_circuit_module(module)

    write_json(out, {
        "instance":      instance.key,
        "backend":       backend,
        "semiring":      semiring,
        "device":        device,
        "nb_vars":       instance.read_nb_vars(),
        "circuit_nodes": cr["circuit_nodes"],
        "circuit_edges": cr.get("circuit_edges"),
        "circuit_depth": cr.get("circuit_depth"),
        "structural":    structural,
    })

    print(
        f"OK  {backend:15s}  {semiring:4s}  {instance.label:50s}"
        f"  relay={structural['relay_fraction']:.1%}"
        f"  dummy_edges={structural['dummy_edge_fraction']:.1%}"
    )
    return 0
