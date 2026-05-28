# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2
"""Compile-stage runner."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from kompyle_bench.compile import compile_one
from kompyle_bench.instance import Instance
from kompyle_bench.paths import compile_result_path
from kompyle_bench.runners._common import skip_if_exists, write_json


def run_compile(
    *,
    exp_id: int,
    instance: Instance,
    backend: str,
    timeout: int,
    mem_mb: int,
    out: Path | None = None,
) -> int:
    """Compile ``instance`` with ``backend``. Returns 0 on success-or-skip."""
    out = out or compile_result_path(exp_id, instance, backend)
    if skip_if_exists(out):
        return 0

    result = compile_one(
        str(instance.cnf_path()),
        backend,
        timeout=timeout,
        mem_mb=mem_mb,
    )
    write_json(out, asdict(result))

    if result.timed_out:
        tag = "TIMEOUT"
    elif result.error:
        tag = f"ERROR: {result.error}"
    else:
        tag = f"OK  {result.compile_s:.2f}s / {result.circuit_nodes}n"
    print(f"{backend:15s}  {instance.label:55s}  →  {tag}")
    return 0
