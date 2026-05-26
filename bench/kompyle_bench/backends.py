# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2
"""Backend registry"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional, Tuple

import kompyle as p
from pysdd.sdd import SddManager


@dataclass(frozen=True)
class CompileOutput:
    """Result of a single compile.

    ``sdd_pair`` is populated only for the ``sdd`` backend.
    """
    circuit: object
    sdd_pair: Optional[Tuple[object, object]] = None    # (mgr, sdd)


# A backend function gets an empty circuit, the CNF path, the cache
# budget in MB (or None to mean "let the backend use its default").
# It returns a CompileOutput whose circuit has had ``set_root`` called.
BackendFn = Callable[[object, str, Optional[int]], CompileOutput]


def _ganak(circuit, cnf_path: str, cache_mb: Optional[int]) -> CompileOutput:
    gopts = p.GanakOptions()
    aopts = p.ArjunOptions()
    aopts.do_arjun = False
    if cache_mb is not None:
        gopts.maximum_cache_size_mb = cache_mb
    root = p.compile_from_cnf_using_ganak(
        circuit, cnf_path,
        ganak_options=gopts, arjun_options=aopts,
    )
    assert root is not None
    circuit.set_root(root)
    return CompileOutput(circuit=circuit)


def _ganak_arjun(circuit, cnf_path: str, cache_mb: Optional[int]) -> CompileOutput:
    opts = p.GanakOptions()
    aopts = p.ArjunOptions()
    aopts.do_arjun = True
    if cache_mb is not None:
        opts.maximum_cache_size_mb = cache_mb
    root = p.compile_from_cnf_using_ganak(
        circuit, cnf_path,
        ganak_options=opts, arjun_options=aopts,
    )
    assert root is not None
    circuit.set_root(root)
    return CompileOutput(circuit=circuit)


def _d4v2(circuit, cnf_path: str, cache_mb: Optional[int]) -> CompileOutput:
    opts = p.D4Options()
    if cache_mb is not None:
        opts.cache_first_page = cache_mb * 1024 * 1024
        # FIXME(Ibrahim): infinite-loop, doesn't crash cleanly
        # opts.cache_extra_page = 0
    root = p.compile_from_cnf_using_d4v2(circuit, cnf_path, options=opts)
    assert root is not None
    circuit.set_root(root)
    return CompileOutput(circuit=circuit)


def _sdd(circuit, cnf_path: str, cache_mb: Optional[int]) -> CompileOutput:

    mgr, sdd = SddManager.from_cnf_file(cnf_path.encode(), vtree_type=b"balanced")
    root = p.compile_from_sdd(circuit, sdd)
    assert root is not None
    circuit.set_root(root)
    return CompileOutput(circuit=circuit, sdd_pair=(mgr, sdd))


BACKENDS: dict[str, BackendFn] = {
    "ganak":       _ganak,
    "ganak_arjun": _ganak_arjun,
    "d4v2":        _d4v2,
    "sdd":         _sdd,
}


def compile_with(
    backend: str,
    cnf_path: str,
    cache_mb: Optional[int] = None,
) -> CompileOutput:
    """Dispatch to the named backend and return its `CompileOutput`.

    Creates a fresh empty circuit.
    Raises `ValueError` if the backend name is unknown.
    """
    if backend not in BACKENDS:
        raise ValueError(
            f"Unknown backend {backend!r}. "
            f"Known: {sorted(BACKENDS)}."
        )
    return BACKENDS[backend](p.Circuit(), cnf_path, cache_mb)
