# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2

import subprocess
import multiprocessing

from pathlib        import Path
from dataclasses    import dataclass
from time           import perf_counter
from typing         import Optional

from util           import _silence_fd, _restore_fd

import kompyle  as p
import klay     as k

TIMEOUT_S   = 300
MEM_MB      = 5000
OVERHEAD_MB = 512


@dataclass
class CompileResult:
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


def _circuit_stats(circuit: p.Circuit):
    # NOTE(Ibrahim): _get_indices removes unused nodes!
    ixs_in, _ = circuit._get_indices()
    nodes = circuit.nb_nodes()
    depth = len(ixs_in)
    edges = sum(len(ix_in) for ix_in in ixs_in)
    return nodes, edges, depth


def _compile_worker(cnf_path: str, backend: str, queue: multiprocessing.Queue,
                    dot_dir, mem_mb: int):
    """
    Runs in its own child process.
    Puts a dict (or exception string) on the queue.
    """
    try:
        circuit = p.Circuit()

        devnull, old_out, old_err = _silence_fd()

        t0 = perf_counter()

        root = None
        cache_mb = mem_mb - OVERHEAD_MB
        if backend == "ganak":
            go = p.GanakOptions()
            go.maximum_cache_size_mb = cache_mb
            # go.do_restart = True
            root = p.compile_from_cnf_using_ganak(circuit, cnf_path,
                                                  ganak_options=go,
                                                  arjun_options=None)

        elif backend == "ganak_arjun":
            go = p.GanakOptions()
            go.maximum_cache_size_mb = cache_mb
            # go.do_restart = True
            ao = p.ArjunOptions()
            root = p.compile_from_cnf_using_ganak(circuit, cnf_path,
                                                  ganak_options=go,
                                                  arjun_options=ao)

        elif backend == "d4v2":
            o = p.D4Options()
            o.cache_first_page = cache_mb * 1024 * 1024
            # FIXME(Ibrahim): infinite-loop, it doesn't not crash cleanly
            # o.cache_extra_page = 0

            root = p.compile_from_cnf_using_d4v2(circuit, cnf_path, options=o)

        elif backend == "sdd":
            root = p.compile_from_cnf_using_sdd(circuit, cnf_path)

        elif backend == "isymganak":
            pass

        elif backend == "isymganak_without_circuit":
            pass

        elif backend == "ganak_without_circuit":
            pass

        else:
            raise ValueError(f"unknown backend {backend}")

        compile_s = perf_counter() - t0

        _restore_fd(devnull, old_out, old_err)

        assert(root is not None)
        circuit.set_root(root)
        nodes, edges, depth = _circuit_stats(circuit)

        if dot_dir is not None:
            stem = Path(cnf_path).stem
            dot_path = Path(dot_dir) / f"{backend}_{stem}.dot"
            svg_path = dot_path.with_suffix(".svg")
            dot_path.parent.mkdir(parents=True, exist_ok=True)
            if not svg_path.exists():
                pass
                # k.klay_ext.circuit_to_dot(circuit, str(dot_path))
                # subprocess.run(
                #     ["dot", "-Tsvg", str(dot_path), "-o", str(svg_path)],
                #     check=True
                # )

        queue.put({
            "ok": True,
            "compile_s": compile_s,
            "circuit_nodes": nodes,
            "circuit_edges": edges,
            "circuit_depth": depth,
        })
    except Exception as e:
        queue.put({"ok": False, "error": str(e)})


def compile_one(cnf_path: str,
                backend: str,
                timeout: int = TIMEOUT_S,
                mem_mb: int = MEM_MB,
                dot_dir=None) -> CompileResult:
    """
    Compile a CNF with one backend.
    """
    nb_vars = nb_clauses = None
    with open(cnf_path) as f:
        for line in f:
            if line.startswith("p cnf"):
                _, _, nb_vars, nb_clauses = line.split()
                break
    if nb_vars is None or nb_clauses is None:
        raise ValueError(f"No 'p cnf' header found in {cnf_path}")
    nb_vars, nb_clauses = int(nb_vars), int(nb_clauses)


    base = dict(backend=backend, cnf=cnf_path, nb_vars=nb_vars, nb_clauses=nb_clauses)
    queue: multiprocessing.Queue = multiprocessing.Queue()
    proc = multiprocessing.Process(
        target=_compile_worker,
        args=(cnf_path, backend, queue, dot_dir, mem_mb),
        # daemon=True,
    )
    proc.start()
    proc.join(timeout)

    if proc.is_alive():
        proc.kill()
        proc.join()
        return CompileResult(**base, compile_s=None, timed_out=True)  # pyright: ignore

    if proc.exitcode != 0 or queue.empty():
        return CompileResult(**base,  # pyright: ignore
                             compile_s=None,
                             error=f"worker exited with code {proc.exitcode}")

    result = queue.get_nowait()
    if not result["ok"]:
        return CompileResult(**base,  # pyright: ignore
                             compile_s=None,
                             error=result["error"])

    return CompileResult(
        **base,  # pyright: ignore
        compile_s=result["compile_s"],
        circuit_nodes=result["circuit_nodes"],
        circuit_edges=result["circuit_edges"],
        circuit_depth=result["circuit_depth"],
    )
