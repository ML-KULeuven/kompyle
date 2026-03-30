# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2

import os
import random
import tempfile
import itertools

from dataclasses import dataclass
from typing      import Dict, Generator, List, Tuple

import klay
import torch
import kompyle as p

# ===================================================================
# CREATE EXAMPLES
# ===================================================================

@dataclass
class FormulaCircuitPair:
    cnf_path: str
    n_vars: int
    clauses: List[List[int]]
    circuit: klay.Circuit
    root: klay.NodePtr
    desc: str
    _tmp: bool = False

    def cleanup(self):
        if self._tmp and os.path.exists(self.cnf_path):
            os.unlink(self.cnf_path)


def write_cnf(n_vars: int,
              clauses: List[List[int]]) -> str:
    fd, path = tempfile.mkstemp(suffix=".cnf")
    with os.fdopen(fd, "w") as f:
        f.write(f"p cnf {n_vars} {len(clauses)}\n")
        for cl in clauses:
            f.write(" ".join(map(str, cl)) + " 0\n")
    return path


def parse_cnf(path: str):
    n_vars, clauses = 0, []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("c"):
                continue
            if line.startswith("p"):
                n_vars = int(line.split()[2])
                continue
            lits = [int(x) for x in line.split() if x != "0"]
            if lits:
                clauses.append(lits)
    return n_vars, clauses


def compile_file(cnf_path: str,
                 desc: str,
                 tmp: bool = False) -> FormulaCircuitPair:
    n_vars, clauses = parse_cnf(cnf_path)
    circuit = klay.Circuit()
    # root = p.compile_from_ganak(circuit, cnf_path)
    root = p.compile_from_ganak_with_arjun(circuit, cnf_path)
    circuit.set_root(root)
    circuit.remove_unused_nodes()
    return FormulaCircuitPair(
        cnf_path=cnf_path,
        n_vars=n_vars,
        clauses=clauses,
        circuit=circuit,
        root=root,
        desc=desc,
        _tmp=tmp,
    )


def compile_inline(n_vars: int,
                   clauses: List[List[int]],
                   desc: str) -> FormulaCircuitPair:
    path = write_cnf(n_vars, clauses)
    return compile_file(path, desc, tmp=True)


def random_clauses(n_vars: int,
                   n_clauses: int,
                   k: int = 3,
                   seed: int = 0) -> List[List[int]]:
    rng = random.Random(seed)
    clauses = []
    for _ in range(n_clauses):
        vs = rng.sample(range(1, n_vars + 1), min(k, n_vars))
        clauses.append([v * rng.choice((-1, 1)) for v in vs])
    return clauses

# ===================================================================
# EVALUATION
# ===================================================================

Assignment = Dict[int, bool]

def all_assignments(n_vars: int) -> Generator[Assignment, None, None]:
    for values in itertools.product([False, True], repeat=n_vars):
        assignment = {}
        for i in range(n_vars):
            assignment[i + 1] = values[i]
        yield assignment


def eval_formula(clauses: List[List[int]], alpha: Assignment) -> bool:
    for clause in clauses:
        clause_satisfied = False

        for literal in clause:
            var = abs(literal)
            value = alpha[var] if literal > 0 else not alpha[var]

            if value:
                clause_satisfied = True
                break

        if not clause_satisfied:
            return False
    return True


def eval_circuit(circuit: klay.Circuit, n_vars: int, alpha: Assignment) -> float:
    pos_w = torch.tensor([1.0 if alpha[v + 1] else 0.0 for v in range(n_vars)])
    m = circuit.to_torch_module(semiring="real")

    # NOTE(Ibrahim):
    # sum because circuits can have multiple roots
    return float(m(pos_w).sum())


def assignment_str(alpha: Assignment) -> str:
    parts = []
    for v, b in sorted(alpha.items()):
        value = "T" if b else "F"
        parts.append(f"x{v}={value}")
    return "{" + ", ".join(parts) + "}"


# ===================================================================
# INTEGRATION (circuit == cnf ?)
# ===================================================================

def assert_exhaustive_equivalence(pair: FormulaCircuitPair) -> None:
    mismatches: List[Tuple[Assignment, bool, bool]] = []
    for alpha in all_assignments(pair.n_vars):
        f_sat  = eval_formula(pair.clauses, alpha)
        c_val  = eval_circuit(pair.circuit, pair.n_vars, alpha)
        c_sat  = c_val > 0.5
        if f_sat != c_sat:
            mismatches.append((alpha, f_sat, c_sat))

    assert not mismatches, (
        f"[{pair.desc}] Exhaustive check found {len(mismatches)} disagreements:\n"
        + "\n".join(
            f"  {assignment_str(a)}: formula={f}, circuit={c}"
            for a, f, c in mismatches[:10]
        )
    )

# ===================================================================
# STRUCTURE (smooth ?, decomposable ?)
# ===================================================================

def assert_decomposable_and_smooth(circuit: klay.Circuit,
                                   label: str = "") -> klay.SDNNFResult:
    result = klay.check_sdnnf(circuit, max_violations=10)
    # result = klay.check_decomposability(circuit, max_violations=10)
    # result = klay.check_smooth(circuit, max_violations=10)
    msg_prefix = f"[{label}] " if (label and ("decomp" in label)) else ""

    assert result.is_decomposable, (
        f"{msg_prefix} circuit is not decomposable.\n{result.summary()}"
    )
    assert result.is_smooth, (
        f"{msg_prefix} circuit is not smooth.\n{result.summary()}"
    )
    assert len(result.violations) == 0, (
        f"{msg_prefix} unexpected violations:\n{result.summary()}"
    )
    return result
