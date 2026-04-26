# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2
"""Compile pysdd Sentential Decision Diagrams into klay circuits.

This module provides the SDD-based compilation path of kompyle:
given a CNF, compile it via pysdd's SDD compiler, then walk the
resulting SDD bottom-up to materialise an equivalent klay circuit.
"""

from __future__ import annotations

import enum
from typing import TYPE_CHECKING, Any, List, Tuple

from klay import NodePtr

if TYPE_CHECKING:
    from pysdd.sdd import SddNode


class _Tag(enum.IntEnum):
    """Internal node-type tag for the iterative SDD traversal."""

    DECISION    = 0
    LITERAL     = 1
    TRUE        = 2
    FALSE       = 3


# =====================================================================
# traversal
# =====================================================================

# NOTE(Ibrahim):
# `_post_order` materialises the entire SDD traversal as a Python list
# before invoking any klay constructor. This keeps the compilation
# loop simple, but also means peak memory grows linearly with SDD
# size. SDDs that don't fit in working memory will OOM here.
# Bounding memory by streaming would re-introduce (worst-case
# exponential) re-traversal, so this is intentional.
def _post_order(root: Any) -> List[Tuple[int, int, Any]]:
    """Linearise an SDD as a post-order list of (tag, id, payload) tuples.

    Walks `root` and visits each node exactly once.
    Decision nodes are emitted *after* their children, so a single
    forward pass over the result lets a consumer build a klay
    circuit bottom-up using just one cache lookup per child.

    The payload field encodes node-specific data:
      - DECISION:    the list of (prime, sub) element pairs.
      - LITERAL:     the integer DIMACS literal.
      - TRUE, FALSE: None.

    Args:
        root: The SDD root node to traverse. Must be non-null.

    Returns:
        A list of `(tag, node_id, payload)` tuples in post-order.
    """
    out: List[Tuple[int, int, Any]] = []
    seen: set = set()
    stack: List[Tuple[Any, bool, Any]] = [(root, False, None)]

    while stack:
        node, visited, payload = stack.pop()

        if visited:
            out.append((_Tag.DECISION, node.id, payload))
            continue

        nid = node.id
        if nid in seen:
            continue
        seen.add(nid)

        if node.is_literal():
            out.append((_Tag.LITERAL, nid, int(node.literal)))
            continue
        if node.is_true():
            out.append((_Tag.TRUE, nid, None))
            continue
        if node.is_false():
            out.append((_Tag.FALSE, nid, None))
            continue

        elements = list(node.elements())
        stack.append((node, True, elements))
        for prime, sub in elements:
            stack.append((sub, False, None))
            stack.append((prime, False, None))

    return out


def compile_from_sdd(circuit, sdd_node) -> NodePtr:
    """Transpile a pysdd SDD into a klay circuit.

    Walks `sdd_node` bottom-up, mapping each SDD node to a klay
    node: literals become literal nodes, decision nodes become
    OR-of-AND structures over their (prime, sub) elements, and the
    True/False constants map to the circuit's True/False sentinels.

    Args:
        circuit: The kompyle/klay Circuit to populate.
                 Must outlive the returned `NodePtr`.
        sdd_node: The SDD root to transpile.

    Returns:
        A `klay.NodePtr` rooted at the compiled circuit. The
        pointer is owned by `circuit`.
    """
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

    cache: dict[int, NodePtr] = {}
    for tag, nid, payload in order:
        if tag == _Tag.DECISION:
            # OR over AND(prime, sub) pairs.
            cache[nid] = _or([_and([cache[p.id], cache[s.id]])
                              for p, s in payload])
        elif tag == _Tag.LITERAL:
            cache[nid] = _lit(payload)
        elif tag == _Tag.TRUE:
            cache[nid] = _TRUE
        else:  # _T_FALSE
            cache[nid] = _FALSE

    return cache[sdd_node.id]


def compile_from_cnf_using_sdd(circuit,
                               cnf_file: str,
                               *,
                               vtree_type: str = "balanced") -> NodePtr:
    """Compile a CNF file into a klay circuit via pysdd.

    Args:
        circuit: The kompyle/klay Circuit to populate.
        cnf_file: Path to a DIMACS CNF file. May be `str` or
            already-encoded `bytes`.
        vtree_type: The vtree shape to use, passed to pysdd. Common
            choices include 'balanced', 'right' and 'left'.

    Returns:
        A `klay.NodePtr` rooted at the compiled circuit.

    Raises:
        ImportError: If pysdd is not installed.
    """
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
