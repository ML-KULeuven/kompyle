# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2
"""Exhaustive equivalence check between a compiled circuit and its source CNF.

For small instances we can enumerate all ``2^n`` assignments and check
that the circuit's truth value agrees with the formula on every input.
This is invaluable for catching backend bugs but blows up exponentially,
so callers should gate on instance size, see `VERIFY_MAX_VARS` / `VERIFY_MAX_CLAUSES`.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass

import torch

VERIFY_MAX_VARS = 30
VERIFY_MAX_CLAUSES = 75

@dataclass
class VerifyInput:
    """Bundle of the data needed to verify a single compile."""
    n_vars: int
    clauses: list[list[int]]
    circuit: object
    desc: str


def _all_assignments(n_vars: int) -> torch.Tensor:
    return torch.tensor(
        list(itertools.product([0.0, 1.0], repeat=n_vars)),
        dtype=torch.float32,
    )


def _eval_formula(clauses: list[list[int]], inputs: torch.Tensor) -> torch.Tensor:
    """Evaluate ``clauses`` on every row of ``inputs`` (shape ``(B, n)``).

    Returns a bool tensor of shape ``(B,)``.
    """
    inputs_bool = inputs > 0.5
    B = inputs.shape[0]
    result = torch.ones(B, dtype=torch.bool)
    for clause in clauses:
        clause_sat = torch.zeros(B, dtype=torch.bool)
        for lit in clause:
            var = abs(lit) - 1
            val = inputs_bool[:, var] if lit > 0 else ~inputs_bool[:, var]
            clause_sat |= val
        result &= clause_sat
    return result


def _eval_circuit(module, inputs: torch.Tensor) -> torch.Tensor:
    outs = []
    for i in range(inputs.shape[0]):
        out = module(inputs[i : i + 1])
        if out.dim() == 0:
            outs.append(out.reshape(1))
        elif out.dim() == 1:
            outs.append(out)
        elif out.dim() == 2:
            outs.append(out.sum(dim=-1))
        else:
            raise RuntimeError(f"Unexpected output shape: {out.shape}")
    return torch.cat(outs, dim=0)


def assert_equivalent(v: VerifyInput) -> None:
    """Raise `AssertionError` if the circuit disagrees with the formula."""
    module = v.circuit.to_torch_module(semiring="real")  # type: ignore[attr-defined]
    module = torch.vmap(module)
    module = torch.compile(module, mode="reduce-overhead")

    inputs = _all_assignments(v.n_vars)
    f_sat = _eval_formula(v.clauses, inputs)
    c_sat = _eval_circuit(module, inputs) > 0.5

    mismatches = f_sat != c_sat
    if mismatches.any():
        idxs = torch.where(mismatches)[0][:10]
        examples = [
            f"{inputs[i].tolist()}: formula={bool(f_sat[i])}, circuit={bool(c_sat[i])}"
            for i in idxs
        ]
        raise AssertionError(
            f"[{v.desc}] exhaustive check found "
            f"{int(mismatches.sum())} disagreements:\n" + "\n".join(examples)
        )


def can_verify(nb_vars: int, nb_clauses: int) -> bool:
    """Cheap predicate so callers can skip verification on big instances."""
    return nb_vars <= VERIFY_MAX_VARS and nb_clauses <= VERIFY_MAX_CLAUSES
