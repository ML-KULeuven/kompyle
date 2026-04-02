# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2

import os
import random
import tempfile
import itertools

from dataclasses import dataclass
from typing      import Dict, Generator, List, Tuple, Callable
from pysdd.sdd   import SddManager, CompilerOptions

import klay as k
import torch
import kompyle as p


def _compile_from_cnf_using_ganak(circuit: k.Circuit, cnf_path: str) -> k.NodePtr:
    return p.compile_from_cnf_using_ganak(circuit, cnf_path)


def _compile_from_cnf_using_ganakarjun(circuit: k.Circuit, cnf_path: str) -> k.NodePtr:
    return p.compile_from_cnf_using_ganakarjun(circuit, cnf_path)


def _compile_from_cnf_using_sdd(circuit: k.Circuit, cnf_path: str) -> k.NodePtr:
    return p.compile_from_cnf_using_sdd(circuit, cnf_path)


def _compile_from_sdd(circuit: k.Circuit, cnf_path: str) -> k.NodePtr:
    mgr, sdd_node = SddManager.from_cnf_file(cnf_path.encode(), vtree_type=b"balanced")
    return p.compile_from_sdd(circuit, sdd_node)


ALL_COMPILERS: List[Tuple[str, Callable]] = [
    # ("from_cnf_using_ganak",        _compile_from_cnf_using_ganak),
    # ("from_cnf_using_ganak_arjun",  _compile_from_cnf_using_ganakarjun),
    # ("from_cnf_using_sdd",          _compile_from_cnf_using_sdd),
    ("from_sdd",                    _compile_from_sdd)
]

COMPILER_IDS   = [name for name, _ in ALL_COMPILERS]
COMPILER_FUNCS = [fn   for _, fn  in ALL_COMPILERS]


# ===================================================================
# CREATE EXAMPLES
# ===================================================================

@dataclass
class FormulaCircuitPair:
    cnf_path: str
    n_vars: int
    clauses: List[List[int]]
    circuit: k.Circuit
    root: k.NodePtr
    desc: str
    compiler_id: str
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


def compile_file(
    cnf_path: str,
    desc: str,
    compiler: Callable,
    compiler_id: str,
    tmp: bool = False,
) -> FormulaCircuitPair:
    n_vars, clauses = parse_cnf(cnf_path)
    circuit = k.Circuit()
    root = compiler(circuit, cnf_path)
    circuit.set_root(root)
    circuit.remove_unused_nodes()
    return FormulaCircuitPair(
        cnf_path=cnf_path,
        n_vars=n_vars,
        clauses=clauses,
        circuit=circuit,
        root=root,
        desc=f"{desc}[{compiler_id}]",
        compiler_id=compiler_id,
        _tmp=tmp,
    )


def compile_inline(
    n_vars: int,
    clauses: List[List[int]],
    desc: str,
    compiler: Callable,
    compiler_id: str,
) -> FormulaCircuitPair:
    path = write_cnf(n_vars, clauses)
    return compile_file(path, desc, compiler, compiler_id, tmp=True)


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


def eval_circuit(circuit: k.Circuit, n_vars: int, alpha: Assignment) -> float:
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

def assert_decomposable(pair: FormulaCircuitPair) -> k.SDNNFResult:
    result = k.check_decomposability(pair.circuit, max_violations=10)
    assert result.is_decomposable, (
        f"[{pair.desc}] circuit is not decomposable.\n{result.summary()}"
    )
    assert len(result.violations) == 0, (
        f"[{pair.desc}] unexpected violations:\n{result.summary()}"
    )

def assert_smooth(pair: FormulaCircuitPair) -> k.SDNNFResult:
    result = k.check_smooth(pair.circuit, max_violations=10)
    assert result.is_smooth, (
        f"[{pair.desc}] circuit is not smooth.\n{result.summary()}"
    )
    assert len(result.violations) == 0, (
        f"[{pair.desc}] unexpected violations:\n{result.summary()}"
    )

def assert_correct_structure(pair: FormulaCircuitPair) -> k.SDNNFResult:
    # result = k.check_sdnnf(circuit, max_violations=10)
    if "ganak" in pair.compiler_id:
        assert_decomposable(pair)
        assert_smooth(pair)
        # check determinisstic
        return

    if "sdd" in pair.compiler_id:
        assert_decomposable(pair)
        # check determinisstic
        return

    raise ValueError("Unknown compiler id given")
