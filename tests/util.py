# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2

import os
import random
import tempfile
import itertools
import subprocess

from dataclasses import dataclass
from typing      import Dict, Generator, List, Tuple, Callable
from pysdd.sdd   import SddManager

import klay as k
import torch
import kompyle as p


# -----------------------------------------------------------------------
# Compilers
# -----------------------------------------------------------------------

def _compile_from_cnf_using_ganak(circuit: p.Circuit, cnf_path: str) -> p.NodePtr:
    return p.compile_from_cnf_using_ganak(circuit, cnf_path)


def _compile_from_cnf_using_ganakarjun(circuit: p.Circuit, cnf_path: str) -> p.NodePtr:
    return p.compile_from_cnf_using_ganakarjun(circuit, cnf_path)


def _compile_from_cnf_using_sdd(circuit: p.Circuit, cnf_path: str) -> p.NodePtr:
    return p.compile_from_cnf_using_sdd(circuit, cnf_path)


def _compile_from_sdd(circuit: p.Circuit, cnf_path: str) -> p.NodePtr:
    mgr, sdd_node = SddManager.from_cnf_file(cnf_path.encode(), vtree_type=b"balanced")
    return p.compile_from_sdd(circuit, sdd_node)


def _compile_from_cnf_using_d4v2(circuit: p.Circuit, cnf_path: str) -> p.NodePtr:
    return p.compile_from_cnf_using_d4v2(circuit, cnf_path)


ALL_COMPILERS: List[Tuple[str, Callable]] = [
    ("from_cnf_using_ganak",        _compile_from_cnf_using_ganak),
    ("from_cnf_using_ganak_arjun",  _compile_from_cnf_using_ganakarjun),
    ("from_cnf_using_sdd",          _compile_from_cnf_using_sdd),
    ("from_sdd",                    _compile_from_sdd),
    ("from_cnf_using_d4v2",         _compile_from_cnf_using_d4v2)
]

COMPILER_IDS   = [name for name, _ in ALL_COMPILERS]
COMPILER_FUNCS = [fn   for _, fn  in ALL_COMPILERS]


# ===================================================================
# CREATE EXAMPLES
# ===================================================================

@dataclass
class FormulaCircuitPair:
    path: str
    n_vars: int
    circuit: p.Circuit
    root: p.NodePtr
    desc: str
    compiler_id: str
    _tmp: bool = False
    _bc: object = None
    _clauses: List[List[int]] = None

    def cleanup(self):
        if self._tmp and os.path.exists(self.path):
            os.unlink(self.path)


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
    circuit = p.Circuit()
    root = compiler(circuit, cnf_path)

    circuit.set_root(root)
    circuit.remove_unused_nodes()

    # dot_path = f"/workspace/tmp/debug_n{n_vars}_m{len(clauses)}_s{0}.dot"
    # k.klay_ext.circuit_to_dot(circuit, dot_path)
    # svg_path = dot_path.replace(".dot", ".svg")
    # subprocess.run(["dot", "-Tsvg", dot_path, "-o", svg_path], check=True)
    # print(f"  → SVG written to {svg_path}")

    assert(circuit.nb_nodes() > 0)
    return FormulaCircuitPair(
        path=cnf_path,
        n_vars=n_vars,
        circuit=circuit,
        root=root,
        desc=f"{desc}[{compiler_id}]",
        compiler_id=compiler_id,
        _tmp=tmp,
        _clauses=clauses,
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
# GATED FORMULA SUPPORT
# ===================================================================

def cnf_to_gated_formula(n_vars: int, clauses: List[List[int]]) -> p.GatedFormula:
    """Encode a CNF as an equivalent GatedFormula.

    The formula is a value independent of any circuit.  Variable "names"
    here are just the stringified integers from the CNF.
    """
    gf = p.GatedFormula()

    for v in range(1, n_vars + 1):
        gf.add_input(str(v))

    next_id = n_vars + 1

    if not clauses:
        assert n_vars >= 1

        tautology_ids = []
        for v in range(1, n_vars + 1):
            gf.add_or(str(next_id), [str(v), str(-v)])
            tautology_ids.append(str(next_id))
            next_id += 1

        gf.add_or(str(next_id), tautology_ids)
        gf.add_target(str(next_id))
        return gf

    clause_vars: List[int] = []
    for clause in clauses:
        gf.add_or(str(next_id), [str(a) for a in clause])
        clause_vars.append(str(next_id))
        next_id += 1

    if len(clause_vars) == 1:
        gf.add_target(clause_vars[0])
        return gf

    gf.add_and(str(next_id), clause_vars)
    gf.add_target(str(next_id))
    return gf


def compile_gated(
    n_vars: int,
    clauses: List[List[int]],
    desc: str,
) -> FormulaCircuitPair:
    gf = cnf_to_gated_formula(n_vars, clauses)
    circuit = p.Circuit()
    root = p.compile_from_gates_formula_using_d4v2(circuit, gf)

    circuit.set_root(root)
    circuit.remove_unused_nodes()

    # dot_path = f"/workspace/tmp/debug_n{n_vars}_m{len(clauses)}_s{1}.dot"
    # k.klay_ext.circuit_to_dot(circuit, dot_path)
    # svg_path = dot_path.replace(".dot", ".svg")
    # subprocess.run(["dot", "-Tsvg", dot_path, "-o", svg_path], check=True)
    # print(f"  → SVG written to {svg_path}")

    assert circuit.nb_nodes() > 0
    return FormulaCircuitPair(
        path="",
        n_vars=n_vars,
        circuit=circuit,
        root=root,
        desc=f"{desc}[gates_d4v2]",
        compiler_id="gates_d4v2",
        _tmp=False,
        _clauses=clauses,
    )


def compile_gated_from_cnf_file(
    cnf_path: str,
    desc: str,
) -> FormulaCircuitPair:
    n_vars, clauses = parse_cnf(cnf_path)
    pair = compile_gated(n_vars, clauses, desc)
    pair.cnf_path = cnf_path
    return pair


def compile_gated_from_bc_file(
    bc_path: str,
    desc: str,
) -> FormulaCircuitPair:
    circuit = p.Circuit()
    root = p.compile_from_gates_file_using_d4v2(circuit, bc_path)

    circuit.set_root(root)
    circuit.remove_unused_nodes()

    assert circuit.nb_nodes() > 0
    bc = parse_bc_file(bc_path)

    # for i, name in enumerate(bc.all_vars):
    #     expected = i + 1
    #     actual = circuit.var_for_name(name)   # idempotent: returns existing id
    #     if actual != expected:
    #         print(f"MISMATCH: {name} expected cid={expected}, got {actual}")

    # dot_path = f"/workspace/tmp/debug_n{len(bc.all_vars)}_s{0}.dot"
    # k.klay_ext.circuit_to_dot(circuit, dot_path)
    # svg_path = dot_path.replace(".dot", ".svg")
    # subprocess.run(["dot", "-Tsvg", dot_path, "-o", svg_path], check=True)
    # print(f"  → SVG written to {svg_path}")

    return FormulaCircuitPair(
        path=bc_path,
        n_vars=len(bc.all_vars),
        circuit=circuit,
        root=root,
        desc=f"{desc}[gates_path_d4v2]",
        compiler_id="gates_path_d4v2",
        _tmp=False,
        _bc=bc
    )

@dataclass
class BcGate:
    gate_type: str
    output: str
    output_negated: bool
    inputs: List[str]
    input_negated: List[bool]


@dataclass
class BcCircuit:
    input_vars: List[str]
    gates: List[BcGate]
    true_lits: List[str]
    true_lits_negated: List[bool]
    all_vars: List[str]

    @property
    def n_input_vars(self) -> int:
        return len(self.input_vars)


def _parse_lit(tok: str) -> Tuple[str, bool]:
    if tok.startswith("-"):
        return tok[1:], True
    return tok, False


def parse_bc_file(path: str) -> BcCircuit:
    input_vars: List[str] = []
    gates: List[BcGate] = []
    true_lits: List[str] = []
    true_lits_negated: List[bool] = []
    all_vars_ordered: List[str] = []
    seen_vars = set()

    def _track_var(name):
        if name not in seen_vars:
            seen_vars.add(name)
            all_vars_ordered.append(name)

    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("c"):
                continue

            parts = line.split()
            kind = parts[0]

            if kind == "I":
                if len(parts) == 2:
                    out_name = parts[1]
                    in_name = parts[1]
                else:
                    raise ValueError(f"malformed identity line: {line}")

                _track_var(out_name)
                inp_name, inp_neg = _parse_lit(in_name)
                _track_var(inp_name)
                input_vars.append(out_name)
                gates.append(BcGate(
                    gate_type="IDENTITY",
                    output=out_name,
                    output_negated=False,
                    inputs=[inp_name],
                    input_negated=[inp_neg],
                ))

            elif kind == "G":
                out_name = parts[1]
                gate_type_char = parts[3]
                gate_type = "AND" if gate_type_char == "A" else "OR"
                _track_var(out_name)
                inp_names, inp_negs = [], []
                for tok in parts[4:]:
                    name, neg = _parse_lit(tok)
                    inp_names.append(name)
                    inp_negs.append(neg)
                    _track_var(name)
                gates.append(BcGate(
                    gate_type=gate_type,
                    output=out_name,
                    output_negated=False,
                    inputs=inp_names,
                    input_negated=inp_negs,
                ))

            elif kind == "T":
                lit_tok = parts[1]
                name, neg = _parse_lit(lit_tok)
                true_lits.append(name)
                true_lits_negated.append(neg)
                _track_var(name)

    return BcCircuit(
        input_vars=input_vars,
        gates=gates,
        true_lits=true_lits,
        true_lits_negated=true_lits_negated,
        all_vars=all_vars_ordered,
    )


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


def eval_circuit(circuit: p.Circuit, n_vars: int, alpha: Assignment) -> float:
    pos_w = torch.tensor([1.0 if alpha[v + 1] else 0.0 for v in range(n_vars)])
    m = circuit.to_torch_module(semiring="real")
    # sum because circuits can have multiple roots
    return float(m(pos_w).sum())


def eval_bc_circuit(bc: BcCircuit, alpha: Assignment) -> bool:
    val = {}
    for i, var_name in enumerate(bc.input_vars):
        val[var_name] = alpha[i + 1]

    for gate in bc.gates:
        if gate.gate_type == "IDENTITY":
            inp = val[gate.inputs[0]]
            if gate.input_negated[0]:
                inp = not inp
            val[gate.output] = inp

        elif gate.gate_type == "AND":
            result = True
            for name, neg in zip(gate.inputs, gate.input_negated):
                v = val[name]
                if neg:
                    v = not v
                if not v:
                    result = False
                    break
            val[gate.output] = result

        elif gate.gate_type == "OR":
            result = False
            for name, neg in zip(gate.inputs, gate.input_negated):
                v = val[name]
                if neg:
                    v = not v
                if v:
                    result = True
                    break
            val[gate.output] = result

    for name, neg in zip(bc.true_lits, bc.true_lits_negated):
        v = val[name]
        if neg:
            v = not v
        if not v:
            return False
    return True


# ===================================================================
# INTEGRATION (circuit == cnf ?)
# ===================================================================

def assignment_str(alpha: Assignment) -> str:
    parts = []
    for v, b in sorted(alpha.items()):
        value = "T" if b else "F"
        parts.append(f"x{v}={value}")
    return "{" + ", ".join(parts) + "}"


def assert_exhaustive_equivalence(pair: FormulaCircuitPair) -> None:
    mismatches: List[Tuple[Assignment, bool, bool]] = []

    if pair._bc is not None:
        input_var_to_circuit_id = {
            var_name: pair._bc.all_vars.index(var_name) + 1
            for var_name in pair._bc.input_vars
        }
        n_input = pair._bc.n_input_vars

        for input_alpha in all_assignments(n_input):
            f_sat = eval_bc_circuit(pair._bc, input_alpha)

            full_alpha = {i: False for i in range(1, pair.n_vars + 1)}
            for i, var_name in enumerate(pair._bc.input_vars):
                cid = input_var_to_circuit_id[var_name]
                full_alpha[cid] = input_alpha[i + 1]

            c_val = eval_circuit(pair.circuit, pair.n_vars, full_alpha)
            c_sat = c_val > 0.5
            if f_sat != c_sat:
                mismatches.append((input_alpha, f_sat, c_sat))
    else:
        for alpha in all_assignments(pair.n_vars):
            f_sat = eval_formula(pair._clauses, alpha)
            c_val = eval_circuit(pair.circuit, pair.n_vars, alpha)
            c_sat = c_val > 0.5
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
    if "ganak" in pair.compiler_id:
        assert_decomposable(pair)
        assert_smooth(pair)
        return

    if "sdd" in pair.compiler_id:
        assert_decomposable(pair)
        return

    if "d4v2" in pair.compiler_id:
        assert_decomposable(pair)
        # TODO(Ibrahim): should be optional
        assert_smooth(pair)
        return

    raise ValueError("Unknown compiler id given")
