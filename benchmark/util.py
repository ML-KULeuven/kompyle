# Copyright (c) 2026 Jaron Maene, Ibrahim El Kaddouri
# Licensed under apachev2

import os
import random
import torch
import itertools

import numpy as np
import kompyle as p

from typing         import List
from dataclasses    import dataclass
from pathlib        import Path

def exp_root(exp_id: int) -> Path:
    return Path(f"exps/exp{exp_id:04d}")

def compile_result_path(exp_id: int, nb_vars, ratio, seed, backend) -> Path:
    return (
        exp_root(exp_id)
        / "results"
        / "compile"
        / backend
        / f"v{nb_vars}_r{ratio:.1f}_s{seed}.json"
    )

def infer_result_path(exp_id: int, nb_vars, ratio, seed, backend, semiring, device) -> Path:
    return (
        exp_root(exp_id)
        / "results"
        / "infer"
        / f"{backend}_{semiring}_{device}"
        / f"v{nb_vars}_r{ratio:.1f}_s{seed}.json"
    )

def experiment_result_path(exp_id: int, nb_vars, ratio, seed, backend, semiring, device) -> Path:
    return (
        exp_root(exp_id)
        / "results" / "experiment" / "dummy_overhead"
        / f"{backend}_{semiring}_{device}"
        / f"v{nb_vars}_r{ratio:.1f}_s{seed}.json"
    )

def _cnf_path(nb_vars: int, ratio: float, seed: int) -> str:
    return f"instances/v{nb_vars}_r{ratio:.1f}_s{seed}.cnf"

def _ensure_cnf(nb_vars: int, ratio: float, seed: int) -> str:
    path = Path(_cnf_path(nb_vars, ratio, seed))
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        generate_random_dimacs(str(path), nb_vars, round(nb_vars * ratio), seed=seed)
    return str(path)

# ---------------------------------------------------------------------------
# CNF-stem-based result paths (for real / non-synthetic instances).
#
# When a CNF is identified by its filesystem path rather than a
# (nb_vars, ratio, seed) triple, we use the file stem as the key so that
# result JSON files land in the same directory tree, just under a different
# name.  All three helpers mirror their synth counterparts exactly.
# ---------------------------------------------------------------------------

def compile_result_path_cnf(exp_id: int, stem: str, backend: str) -> Path:
    return (
        exp_root(exp_id)
        / "results"
        / "compile"
        / backend
        / f"{stem}.json"
    )

def infer_result_path_cnf(exp_id: int, stem: str, backend: str,
                           semiring: str, device: str) -> Path:
    return (
        exp_root(exp_id)
        / "results"
        / "infer"
        / f"{backend}_{semiring}_{device}"
        / f"{stem}.json"
    )

def experiment_result_path_cnf(exp_id: int, stem: str, backend: str,
                                semiring: str, device: str) -> Path:
    return (
        exp_root(exp_id)
        / "results" / "experiment" / "dummy_overhead"
        / f"{backend}_{semiring}_{device}"
        / f"{stem}.json"
    )

def read_nb_vars_from_cnf(cnf_path: str) -> int:
    """Read the number of variables from a DIMACS CNF header."""
    with open(cnf_path) as f:
        for line in f:
            if line.startswith("p cnf"):
                return int(line.split()[2])
    raise ValueError(f"No 'p cnf' header found in {cnf_path}")



def generate_random_dimacs(file_name: str, var_count: int, 
                           clause_count: int, seed: int = 1, clause_length: int = 3):
    """
    Generate a random k-CNF formula and save it to a file in DIMACS format.
    """
    random.seed(seed)

    with open(file_name, "w") as f:
        f.write(f"p cnf {var_count} {clause_count}\n")
        for _ in range(clause_count):
            clause = [random.randint(1, var_count) * random.choice([1, -1])
                        for _ in range(clause_length)]
            f.write(" ".join(map(str, clause)) + " 0\n")


def plot_circuit_overhead(module):
    layer_widths = []
    layer_edges = []
    for layer in module.layers:
        layer_width = layer.csr.shape[0] - 1
        layer_widths.append(layer_width)
        layer_edges.append(layer.ptrs.shape[0])

    xx = list(range(len(layer_widths)))
    import matplotlib.pyplot as plt
    plt.plot(layer_widths)
    plt.plot(layer_edges)
    plt.fill_between(xx, layer_widths, alpha=0.2, label="overhead")
    plt.fill_between(xx, layer_widths, layer_edges, alpha=0.2, label="useful computation")
    plt.legend(["width", "edges"])
    plt.title("Layer utilization")
    # plt.yscale("log")
    plt.xlabel("Layer")
    plt.show()


def numpy_weights(nb_vars: int, semiring: str, batch_size: int):
    weights = np.random.uniform(size=(batch_size, nb_vars)).astype(np.float32)
    neg_weights = 1 - weights
    if semiring == "log":
        weights = np.log(weights)
        neg_weights = np.log(neg_weights)
    return weights, neg_weights


def python_weights(nb_vars: int, semiring: str):
    weights, neg_weights = numpy_weights(nb_vars, semiring, batch_size=1)
    return weights[0].tolist(), neg_weights[0].tolist()


def _silence_fd():
    devnull = os.open(os.devnull, os.O_WRONLY)
    old_stdout = os.dup(1)
    old_stderr = os.dup(2)

    os.dup2(devnull, 1)
    os.dup2(devnull, 2)

    return devnull, old_stdout, old_stderr


def _restore_fd(devnull, old_stdout, old_stderr):
    os.dup2(old_stdout, 1)
    os.dup2(old_stderr, 2)
    os.close(devnull)
    os.close(old_stdout)
    os.close(old_stderr)


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

def all_assignments_tensor(n_vars: int) -> torch.Tensor:
    return torch.tensor(
        list(itertools.product([0.0, 1.0], repeat=n_vars)),
        dtype=torch.float32
    )

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


def assert_exhaustive_equivalence(pair: FormulaCircuitPair) -> None:
    module = pair.circuit.to_torch_module(semiring="real")
    module = torch.vmap(module)
    module = torch.compile(module, mode="reduce-overhead")

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
