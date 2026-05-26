# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2
"""Count-stage runner."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from kompyle_bench.count import count_one
from kompyle_bench.instance import Instance
from kompyle_bench.paths import count_result_path
from kompyle_bench.runners._common import skip_if_exists, write_json


def run_count(
    *,
    exp_id:   int,
    instance: Instance,
    backend:  str,
    timeout:  int,
    mem_mb:   int,
    out:      Path | None = None,
) -> int:
    """Run a count-only benchmark for ``instance`` × ``backend``.

    Returns 0 on success-or-skip (mirroring run_compile semantics).
    """
    out = out or count_result_path(exp_id, instance, backend)
    if skip_if_exists(out):
        return 0

    result = count_one(
        str(instance.cnf_path()), backend, timeout=timeout, mem_mb=mem_mb,
    )
    write_json(out, asdict(result))

    if result.timed_out:
        tag = "TIMEOUT"
    elif result.error:
        tag = f"ERROR: {result.error}"
    else:
        mc = result.model_count or "?"
        # Truncate huge counts so the log line stays readable.
        if len(mc) > 12:
            mc = f"{mc[:9]}...({len(mc)} digits)"
        tag = f"OK  {result.count_s:.2f}s  count={mc}"
    print(f"{backend:20s}  {instance.label:55s}  ->  {tag}")
    return 0
