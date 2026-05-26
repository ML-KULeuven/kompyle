# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2
"""Inference-stage runner."""

from __future__ import annotations

from kompyle_bench.backends import compile_with
from kompyle_bench.benchmarks import benchmark_klay_torch, benchmark_pysdd
from kompyle_bench.instance import Instance
from kompyle_bench.io import silenced_fds, parse_cnf
from kompyle_bench.paths import compile_result_path, infer_result_path
from kompyle_bench.runners._common import (
    load_compile_result,
    skip_if_exists,
    write_json,
)
from kompyle_bench.verify import VerifyInput, assert_equivalent, can_verify


def run_infer(
    *,
    exp_id:     int,
    instance:   Instance,
    backend:    str,
    semiring:   str,
    device:     str,
    batch_size: int,
    nb_repeats: int,
    verify:     bool,
) -> int:
    """Inference benchmark for one parameter combination.

    Returns 0 on success-or-skip, 1 on error.
    """
    cp = compile_result_path(exp_id, instance, backend)
    cr = load_compile_result(cp)
    if cr is None:
        return 0 if cp.exists() else 1

    out = infer_result_path(exp_id, instance, backend, semiring, device)
    if skip_if_exists(out):
        return 0

    cnf = str(instance.cnf_path())
    with silenced_fds():
        compile_out = compile_with(backend, cnf)

    if verify:
        nb_vars, clauses = parse_cnf(cnf)
        if can_verify(nb_vars, len(clauses)):
            v = VerifyInput(
                n_vars=nb_vars,
                clauses=clauses,
                circuit=compile_out.circuit,
                desc=f"{backend}[verify] {instance.label}",
            )
            try:
                assert_equivalent(v)
                print(f"[verify] OK  {backend}  {instance.label}")
            except AssertionError as e:
                print(f"[verify] FAIL  {e}")
                return 1

    nb_vars = instance.read_nb_vars()
    results: dict = {"circuit_nodes": cr["circuit_nodes"]}
    results.update(benchmark_klay_torch(
        compile_out.circuit,
        nb_vars,
        semiring,
        nb_repeats=nb_repeats,
        device=device,
        batch_size=batch_size,
    ))
    if compile_out.sdd_pair is not None:
        _, sdd = compile_out.sdd_pair
        results["pysdd"] = benchmark_pysdd(sdd, nb_vars, semiring)

    write_json(out, results)
    print(
        f"OK  {backend:15s}  {semiring:4s}  {instance.label:50s}  device={device}"
    )
    return 0
