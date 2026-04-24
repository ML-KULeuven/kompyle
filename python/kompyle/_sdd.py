# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2
"""Python implementation of the SDD -> klay compilation path."""

from __future__ import annotations
from typing import Any, List, Tuple
from klay import NodePtr


_T_DECISION = 0
_T_LITERAL  = 1
_T_TRUE     = 2
_T_FALSE    = 3


# =====================================================================
# traversal
# =====================================================================

# NOTE(Ibrahim):
# unbounded in memory consumption.
# all circuits need to be able to fit in working memory
# bounding memory has as a consequence exponential behaviour!
def _post_order(root: Any) -> List[Tuple[int, int, Any]]:
    out: List[Tuple[int, int, Any]] = []
    seen: set = set()
    stack: List[Tuple[Any, bool, Any]] = [(root, False, None)]

    while stack:
        node, visited, payload = stack.pop()

        if visited:
            out.append((_T_DECISION, node.id, payload))
            continue

        nid = node.id
        if nid in seen:
            continue
        seen.add(nid)

        if node.is_literal():
            out.append((_T_LITERAL, nid, int(node.literal)))
            continue
        if node.is_true():
            out.append((_T_TRUE, nid, None))
            continue
        if node.is_false():
            out.append((_T_FALSE, nid, None))
            continue

        elements = list(node.elements())
        stack.append((node, True, elements))
        for prime, sub in elements:
            stack.append((sub, False, None))
            stack.append((prime, False, None))

    return out


def compile_from_sdd(circuit, sdd_node) -> NodePtr:
    if sdd_node.is_true():
        return circuit.true_node()
    if sdd_node.is_false():
        return circuit.false_node()
    if sdd_node.is_literal():
        return circuit.literal_node(int(sdd_node.literal))

    order = _post_order(sdd_node)

    _and    = circuit.and_node
    _or     = circuit.or_node
    _lit    = circuit.literal_node
    _TRUE   = circuit.true_node()
    _FALSE  = circuit.false_node()

    cache: dict = {}

    for tag, nid, payload in order:
        if tag == _T_DECISION:
            # OR over AND(prime, sub) pairs.
            cache[nid] = _or([_and([cache[p.id], cache[s.id]])
                              for p, s in payload])
        elif tag == _T_LITERAL:
            cache[nid] = _lit(payload)
        elif tag == _T_TRUE:
            cache[nid] = _TRUE
        else:  # _T_FALSE
            cache[nid] = _FALSE

    return cache[sdd_node.id]


def compile_from_cnf_using_sdd(circuit,
                               cnf_file: str,
                               *,
                               vtree_type: str = "balanced") -> NodePtr:
    try:
        from pysdd.sdd import SddManager
    except ImportError as e:
        raise ImportError(
            "pysdd is required for SDD-based compilation. "
            "Install it with:   pip install kompyle[sdd]"
        ) from e

    cnf_bytes = cnf_file.encode() if isinstance(cnf_file, str) else cnf_file
    vt_bytes  = vtree_type.encode() if isinstance(vtree_type, str) else vtree_type

    manager, root = SddManager.from_cnf_file(cnf_bytes, vtree_type=vt_bytes)
    try:
        return compile_from_sdd(circuit, root)
    finally:
        del root
        del manager


__all__ = ["compile_from_sdd", "compile_from_cnf_using_sdd"]
