# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2
"""kompyle: knowledge-compilation pipeline into klay circuits.
 
Provides entry points for compiling Boolean formulas expressed as CNF files,
gate-based formulas, or pre-built SDD nodes into klay d-DNNF circuits.

Typical usage::

    import kompyle

    circuit = kompyle.Circuit()

    # Ganak:
    root = kompyle.compile_from_cnf_using_ganak(circuit, "formula.cnf")

    # Ganak with counter options:
    g_opts = kompyle.GanakOptions()
    g_opts.verb = 1
    root = kompyle.compile_from_cnf_using_ganak(circuit, "formula.cnf",
                                                ganak_options=g_opts)

    # Ganak with Arjun pre-pass:
    a_opts = kompyle.ArjunOptions()
    root = kompyle.compile_from_cnf_using_ganak(
        circuit, "formula.cnf",
        ganak_options=g_opts,
        arjun_options=a_opts,
    )

    # D4v2:
    d4_opts = kompyle.D4Options()
    d4_opts.preproc_method = kompyle.D4PreprocMethod.Equiv
    d4_opts.solver = kompyle.D4Solver.Glucose
    root = kompyle.compile_from_cnf_using_d4v2(circuit, "formula.cnf",
                                               options=d4_opts)

    result = kompyle.check_sdnnf(root)
"""

from __future__ import annotations

import ctypes
import glob
import os
import sys

# ---------------------------------------------------------------------------
# Preload libklay.so with RTLD_GLOBAL.
#
# On Linux, ctypes.CDLL with RTLD_GLOBAL makes the library's symbols
# globally visible in the process's dynamic-linker namespace. When
# pkompyle.abi3.so is loaded, its DT_NEEDED entry for libklay.so is
# satisfied from that global table, no filesystem search needed, and
# no duplicate copy is loaded.
#
# On macOS the global-symbol mechanism is less strictly necessary
# (dyld resolves across RPATH handles differently), but loading first
# is correct.
#
# Windows (.pyd) relies on DLL search order rather than RTLD_GLOBAL.
# The ctypes load below is still useful because it adds the klay
# package directory to the DLL search path via os.add_dll_directory.
# ---------------------------------------------------------------------------
def _preload_libklay() -> None:
    """Load libklay into the global symbol namespace.

    Locates libklay inside the installed klay package directory, then
    calls ctypes.CDLL with RTLD_GLOBAL so that all downstream C
    extensions (including pkompyle.abi3.so) resolve libklay symbols
    against the same already-loaded library rather than loading their
    own copy.

    Silently does nothing if klay is not importable
    """
    try:
        import klay as _klay_pkg
    except ImportError:
        return

    klay_dir = os.path.dirname(os.path.abspath(_klay_pkg.__file__))

    if sys.platform == "win32":
        # On Windows, add the directory so Windows' LoadLibrary can
        # find the DLL transitively, ctypes.CDLL handles the rest.
        os.add_dll_directory(klay_dir)
        patterns = [os.path.join(klay_dir, "klay*.dll")]
    elif sys.platform == "darwin":
        patterns = [
            os.path.join(klay_dir, "libklay*.dylib"),
            os.path.join(klay_dir, "libklay*.so"),
        ]
    else:
        patterns = [os.path.join(klay_dir, "libklay*.so*")]

    for pattern in patterns:
        candidates = glob.glob(pattern)
        if not candidates:
            continue
        candidates.sort(key=lambda p: (p.count(".so."), p))
        lib_path = candidates[0]
        mode = (
            ctypes.RTLD_GLOBAL if sys.platform != "win32"
            else ctypes.DEFAULT_MODE
        )
        ctypes.CDLL(lib_path, mode=mode)
        return


_preload_libklay()


from klay import (  # noqa: E402
    NodePtr,
    check_sdnnf,
    check_decomposability,
    check_smooth,
    SDNNFResult,
    SDNNFViolation,
)

from .pkompyle import (  # noqa: E402
    # Core types
    Circuit,
    GatedFormula,
    # Option types
    GanakOptions,
    ArjunOptions,
    D4Options,
    D4PreprocMethod,
    D4Solver,
    # Compile entry points
    compile_from_cnf_using_ganak,
    compile_from_cnf_using_d4v2,
    compile_from_gates_file_using_d4v2,
    compile_from_gates_formula_using_d4v2,
)

from ._sdd import (  # noqa: E402
    compile_from_sdd,
    compile_from_cnf_using_sdd,
)

__all__ = [
    # kompyle core
    "Circuit",
    "GatedFormula",
    # Solver option types
    "GanakOptions",
    "ArjunOptions",
    "D4Options",
    "D4PreprocMethod",
    "D4Solver",
    # compile entry points
    "compile_from_cnf_using_ganak",
    "compile_from_cnf_using_sdd",
    "compile_from_sdd",
    "compile_from_cnf_using_d4v2",
    "compile_from_gates_file_using_d4v2",
    "compile_from_gates_formula_using_d4v2",
    # re-exports from klay
    "NodePtr",
    "check_sdnnf",
    "check_decomposability",
    "check_smooth",
    "SDNNFResult",
    "SDNNFViolation",
]
