# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2
"""Process-isolated count run with wall-clock timeout.

Mirror of `kompyle_bench.compile` for count-only backends.
We use the same isolation pattern (subprocess + mp.Queue + join-with-
timeout) so behaviour is uniform. A runaway counter gets killed by the
parent, never takes the harness down with it.
"""

from __future__ import annotations

import multiprocessing as mp
from dataclasses import dataclass
from time import perf_counter
from typing import Optional

from kompyle_bench.counters import count_with
from kompyle_bench.io import silenced_fds


DEFAULT_TIMEOUT_S = 300
DEFAULT_MEM_MB = 5000
# Compile-time overhead beyond the cache itself (Python interpreter,
# library code, etc.). Subtracted from --mem-mb before handing the
# budget to the backend. Mirrors kompyle_bench.compile.OVERHEAD_MB.
OVERHEAD_MB = 512


@dataclass
class CountResult:
    """JSON-serialisable record of a count attempt."""
    backend:     str
    cnf:         str
    nb_vars:     int
    nb_clauses:  int
    count_s:     Optional[float]
    model_count: Optional[str]
    timed_out:   bool = False
    error:       Optional[str] = None


def _read_cnf_header(cnf_path: str) -> tuple[int, int]:
    with open(cnf_path) as f:
        for line in f:
            if line.startswith("p cnf"):
                _, _, nv, nc = line.split()
                return int(nv), int(nc)
    raise ValueError(f"No 'p cnf' header in {cnf_path}")


def _worker(cnf_path: str, backend: str, cache_mb: int, queue: mp.Queue) -> None:
    try:
        with silenced_fds():
            t0 = perf_counter()
            out = count_with(backend, cnf_path, cache_mb=cache_mb)
            count_s = perf_counter() - t0
        queue.put({
            "ok": True,
            "count_s":     count_s,
            "model_count": None if out.model_count is None else str(out.model_count),
        })
    except Exception as e:
        queue.put({"ok": False, "error": str(e)})


def count_one(
    cnf_path: str,
    backend: str,
    timeout: int = DEFAULT_TIMEOUT_S,
    mem_mb: int = DEFAULT_MEM_MB,
) -> CountResult:
    """Run ``backend`` on ``cnf_path`` in an isolated subprocess."""
    nb_vars, nb_clauses = _read_cnf_header(cnf_path)
    base = dict(backend=backend, cnf=cnf_path,
                nb_vars=nb_vars, nb_clauses=nb_clauses)

    queue: mp.Queue = mp.Queue()
    proc = mp.Process(
        target=_worker,
        args=(cnf_path, backend, mem_mb - OVERHEAD_MB, queue),
    )
    proc.start()
    proc.join(timeout)

    if proc.is_alive():
        proc.kill()
        proc.join()
        return CountResult(**base,  # type: ignore[arg-type]
                           count_s=None,
                           model_count=None,
                           timed_out=True)

    if proc.exitcode != 0 or queue.empty():
        return CountResult(
            **base,  # type: ignore[arg-type]
            count_s=None,
            model_count=None,
            error=f"worker exited with code {proc.exitcode}",
        )

    result = queue.get_nowait()
    if not result["ok"]:
        return CountResult(
            **base,  # type: ignore[arg-type]
            count_s=None,
            model_count=None,
            error=result["error"],
        )
    return CountResult(
        **base,  # type: ignore[arg-type]
        count_s=result["count_s"],
        model_count=result["model_count"],
    )
