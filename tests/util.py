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

import torch
import kompyle  as p
import klay     as k


# -----------------------------------------------------------------------
# Compilers
# -----------------------------------------------------------------------

def _compile_from_cnf_using_ganak(circuit: p.Circuit, cnf_path: str) -> p.NodePtr:
    return p.compile_from_cnf_using_ganak(circuit, cnf_path, arjun_options=None)


def _compile_from_cnf_using_ganak_arjun(circuit: p.Circuit, cnf_path: str) -> p.NodePtr:
    ao = p.ArjunOptions()
    return p.compile_from_cnf_using_ganak(circuit, cnf_path, arjun_options=ao)


def _compile_from_cnf_using_sdd(circuit: p.Circuit, cnf_path: str) -> p.NodePtr:
    return p.compile_from_cnf_using_sdd(circuit, cnf_path)


def _compile_from_sdd(circuit: p.Circuit, cnf_path: str) -> p.NodePtr:
    mgr, sdd_node = SddManager.from_cnf_file(cnf_path.encode(), vtree_type=b"balanced")
    return p.compile_from_sdd(circuit, sdd_node)


def _compile_from_cnf_using_d4v2(circuit: p.Circuit, cnf_path: str) -> p.NodePtr:
    return p.compile_from_cnf_using_d4v2(circuit, cnf_path)


ALL_COMPILERS: List[Tuple[str, Callable]] = [
    ("from_cnf_using_ganak",        _compile_from_cnf_using_ganak),
    ("from_cnf_using_ganak_arjun",  _compile_from_cnf_using_ganak_arjun),
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

@dataclass
class FormulaCircuitPair:
    path: str
    n_vars: int
    circuit: p.Circuit
    root: p.NodePtr
    desc: str
    compiler_id: str
    _tmp: bool = False
    _bc: BcCircuit | None = None
    _clauses: List[List[int]] | None = None

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

    # dot_path = f"./tmp/debug_cnf_{compiler_id}_n{n_vars}_m{len(clauses)}.dot"
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

    clause_vars: List[str] = []
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

    # dot_path = f"./tmp/debug_gated_d4v2_n{n_vars}_m{len(clauses)}.dot"
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
    pair.path = cnf_path
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

    # dot_path = f"./tmp/debug_bcfile_d4v2_n{len(bc.all_vars)}.dot"
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


def all_assignments_tensor(n_vars: int) -> torch.Tensor:
    return torch.tensor(
        list(itertools.product([0.0, 1.0], repeat=n_vars)),
        dtype=torch.float32
    )


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


def eval_formula_batch(clauses, inputs: torch.Tensor) -> torch.Tensor:
    """
    inputs: (B, n) in {0,1}
    returns: (B,) bool
    """
    inputs_bool = inputs > 0.5
    B = inputs.shape[0]
    result = torch.ones(B, dtype=torch.bool)

    for clause in clauses:
        clause_sat = torch.zeros(B, dtype=torch.bool)
        for lit in clause:
            var = abs(lit) - 1
            if lit > 0:
                val = inputs_bool[:, var]
            else:
                val = ~inputs_bool[:, var]
            clause_sat |= val
        result &= clause_sat
    return result


def eval_circuit_batch(module, inputs: torch.Tensor) -> torch.Tensor:
    """
    inputs: (B, n)
    returns: (B,) float, one value per assignment
    """
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

def eval_bc_circuit_batch(bc: BcCircuit, inputs: torch.Tensor) -> torch.Tensor:
    """
    inputs: (B, n_input_vars)
    returns: (B,) bool
    """
    inputs_bool = inputs > 0.5
    B = inputs.shape[0]

    val: Dict[str, torch.Tensor] = {}

    for i, var_name in enumerate(bc.input_vars):
        val[var_name] = inputs_bool[:, i]

    for gate in bc.gates:
        if gate.gate_type == "IDENTITY":
            x = val[gate.inputs[0]]
            if gate.input_negated[0]:
                x = ~x
            val[gate.output] = x

        elif gate.gate_type == "AND":
            x = torch.ones(B, dtype=torch.bool)
            for name, neg in zip(gate.inputs, gate.input_negated):
                v = val[name]
                if neg:
                    v = ~v
                x &= v
            val[gate.output] = x

        elif gate.gate_type == "OR":
            x = torch.zeros(B, dtype=torch.bool)
            for name, neg in zip(gate.inputs, gate.input_negated):
                v = val[name]
                if neg:
                    v = ~v
                x |= v
            val[gate.output] = x

    result = torch.ones(B, dtype=torch.bool)
    for name, neg in zip(bc.true_lits, bc.true_lits_negated):
        v = val[name]
        if neg:
            v = ~v
        result &= v
    return result


# ===================================================================
# INTEGRATION (circuit == cnf ?)
# ===================================================================

def assert_exhaustive_equivalence(pair: FormulaCircuitPair) -> None:
    module = pair.circuit.to_torch_module(semiring="real")
    module = torch.vmap(module)
    module = torch.compile(module, mode="reduce-overhead")

    if pair._bc is not None:
        bc = pair._bc
        inputs = all_assignments_tensor(bc.n_input_vars)
        f_sat = eval_bc_circuit_batch(bc, inputs)
        full_inputs = torch.zeros((inputs.shape[0], pair.n_vars))
        input_var_to_circuit_id = {
            var_name: bc.all_vars.index(var_name)
            for var_name in bc.input_vars
        }

        for i, var_name in enumerate(bc.input_vars):
            cid = input_var_to_circuit_id[var_name]
            full_inputs[:, cid] = inputs[:, i]

        c_vals = eval_circuit_batch(module, full_inputs)
        c_sat = c_vals > 0.5

    else:
        assert pair._clauses is not None
        inputs = all_assignments_tensor(pair.n_vars)
        f_sat = eval_formula_batch(pair._clauses, inputs)
        c_vals = eval_circuit_batch(module, inputs)
        c_sat = c_vals > 0.5

    mismatches = (f_sat != c_sat)

    if mismatches.any():
        idxs = torch.where(mismatches)[0][:10]

        examples = []
        for i in idxs:
            a = inputs[i]
            examples.append(
                f"{a.tolist()}: formula={bool(f_sat[i])}, circuit={bool(c_sat[i])}"
            )

        raise AssertionError(
            f"[{pair.desc}] Exhaustive check found {mismatches.sum().item()} disagreements:\n"
            + "\n".join(examples)
        )

# ===================================================================
# STRUCTURE (smooth ?, decomposable ?)
# ===================================================================

def assert_decomposable(pair: FormulaCircuitPair) -> p.SDNNFResult:
    result = p.check_decomposability(pair.circuit, max_violations=10)
    assert result.is_decomposable, (
        f"[{pair.desc}] circuit is not decomposable.\n{result.summary()}"
    )
    assert len(result.violations) == 0, (
        f"[{pair.desc}] unexpected violations:\n{result.summary()}"
    )

def assert_smooth(pair: FormulaCircuitPair) -> p.SDNNFResult:
    result = p.check_smooth(pair.circuit, max_violations=10)
    assert result.is_smooth, (
        f"[{pair.desc}] circuit is not smooth.\n{result.summary()}"
    )
    assert len(result.violations) == 0, (
        f"[{pair.desc}] unexpected violations:\n{result.summary()}"
    )

def assert_correct_structure(pair: FormulaCircuitPair) -> p.SDNNFResult:
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
