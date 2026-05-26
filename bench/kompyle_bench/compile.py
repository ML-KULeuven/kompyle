# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2
"""Process-isolated compile with wall-clock timeout.

Each backend runs in its own subprocess so that a runaway compile can
be killed without taking the harness down with it. The child puts a
result dict on a `multiprocessing.Queue` which the parent harvests.
"""

from __future__ import annotations

import multiprocessing as mp
from dataclasses import dataclass
from time import perf_counter
from typing import Optional

from kompyle_bench.backends import compile_with
from kompyle_bench.io import silenced_fds


DEFAULT_TIMEOUT_S = 300
DEFAULT_MEM_MB = 5000

# NOTE(Ibrahim):
# compile overhead beyond the cache itself (Python interpreter, library
# code, etc.). Subtracted from --mem-mb before handing the budget to
# the backend.
OVERHEAD_MB = 512


@dataclass
class CompileResult:
    """JSON-serialisable record of a compile attempt."""
    backend: str
    cnf: str
    nb_vars: int
    nb_clauses: int
    compile_s: Optional[float]
    timed_out: bool = False
    error: Optional[str] = None
    circuit_nodes: Optional[int] = None
    circuit_edges: Optional[int] = None
    circuit_depth: Optional[int] = None


def _circuit_stats(circuit) -> tuple[int, int, int]:
    """``(nodes, edges, depth)`` after dropping unused nodes."""
    # NOTE(Ibrahim): _get_indices removes unused nodes.
    ixs_in, _ = circuit._get_indices()
    nodes = circuit.nb_nodes()
    depth = len(ixs_in)
    edges = sum(len(ix_in) for ix_in in ixs_in)
    return nodes, edges, depth


def _read_cnf_header(cnf_path: str) -> tuple[int, int]:
    """Read ``(nb_vars, nb_clauses)`` from the DIMACS ``p cnf`` header."""
    with open(cnf_path) as f:
        for line in f:
            if line.startswith("p cnf"):
                _, _, nb_vars, nb_clauses = line.split()
                return int(nb_vars), int(nb_clauses)
    raise ValueError(f"No 'p cnf' header in {cnf_path}")


def _worker(cnf_path: str, backend: str, cache_mb: int, queue: mp.Queue) -> None:
    """Subprocess entry point. Puts a dict on ``queue`` and exits."""
    try:
        with silenced_fds():
            t0 = perf_counter()
            out = compile_with(backend, cnf_path, cache_mb=cache_mb)
            compile_s = perf_counter() - t0
            nodes, edges, depth = _circuit_stats(out.circuit)

        queue.put({
            "ok": True,
            "compile_s": compile_s,
            "circuit_nodes": nodes,
            "circuit_edges": edges,
            "circuit_depth": depth,
        })
    except Exception as e:
        queue.put({"ok": False, "error": str(e)})


def compile_one(
    cnf_path: str,
    backend: str,
    timeout: int = DEFAULT_TIMEOUT_S,
    mem_mb: int = DEFAULT_MEM_MB,
) -> CompileResult:
    """Compile one CNF in an isolated subprocess.

    On timeout the subprocess is killed and a result with
    ``timed_out=True`` is returned. On crash, ``error`` is populated.
    """
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
        return CompileResult(**base,  # type: ignore[arg-type]
                             compile_s=None,
                             timed_out=True)

    if proc.exitcode != 0 or queue.empty():
        return CompileResult(
            **base, compile_s=None,  # type: ignore[arg-type]
            error=f"worker exited with code {proc.exitcode}",
        )

    result = queue.get_nowait()
    if not result["ok"]:
        return CompileResult(**base,  # type: ignore[arg-type]
                             compile_s=None,
                             error=result["error"])

    return CompileResult(
        **base,  # type: ignore[arg-type]
        compile_s=result["compile_s"],
        circuit_nodes=result["circuit_nodes"],
        circuit_edges=result["circuit_edges"],
        circuit_depth=result["circuit_depth"],
    )
