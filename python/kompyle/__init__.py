# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2
"""kompyle, knowledge-compilation pipeline into klay circuits."""

from klay import (
    NodePtr,
    check_sdnnf,
    check_decomposability,
    check_smooth,
    SDNNFResult,
    SDNNFViolation,
)

from .pkompyle import (
    Circuit,
    GatedFormula,
    compile_from_cnf_using_ganak,
    compile_from_cnf_using_ganakarjun,
    compile_from_cnf_using_d4v2,
    compile_from_gates_file_using_d4v2,
    compile_from_gates_formula_using_d4v2,
)

from ._sdd import (
    compile_from_sdd,
    compile_from_cnf_using_sdd,
)

__all__ = [
    # kompyle core
    "Circuit",
    "GatedFormula",
    # compile entry points
    "compile_from_cnf_using_ganak",
    "compile_from_cnf_using_ganakarjun",
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
