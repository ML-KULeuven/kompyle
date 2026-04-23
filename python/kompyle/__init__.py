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
    compile_from_cnf_using_sdd,
    compile_from_cnf_using_d4v2,
    compile_from_gates_file_using_d4v2,
    compile_from_gates_formula_using_d4v2,
    compile_from_sdd,
    _compile_from_sdd_raw
)

from .sdd_transform import sdd_to_klay
# from ./sdd_bridge.pyx import _sdd_node_ptr

# return _compile_from_sdd_raw(_sdd_node_ptr(node))
def compile_from_sdd_cpp(circuit, node):
    return compile_from_sdd(circuit, node)

def compile_from_sdd_py(circuit, node):
    return sdd_to_klay(circuit, node)


__all__ = [
    # kompyle core
    "Circuit",
    "GatedFormula",
    # compile entry points
    "compile_from_cnf_using_ganak",
    "compile_from_cnf_using_ganakarjun",
    "compile_from_cnf_using_sdd",
    "compile_from_sdd",
    "compile_from_sdd_py",
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
