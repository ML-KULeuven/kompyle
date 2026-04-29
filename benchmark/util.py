# Copyright (c) 2026 Jaron Maene, Ibrahim El Kaddouri
# Licensed under apachev2

import os
import random

import numpy as np

from pathlib import Path

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

def experiment_result_path(nb_vars, ratio, seed, backend, semiring, device) -> Path:
    return Path(
        f"results/experiment/dummy_overhead"
        f"/{backend}_{semiring}_{device}"
        f"/v{nb_vars}_r{ratio:.1f}_s{seed}.json"
    )

def _cnf_path(nb_vars: int, ratio: float, seed: int) -> str:
    return f"instances/v{nb_vars}_r{ratio:.1f}_s{seed}.cnf"

def _ensure_cnf(nb_vars: int, ratio: float, seed: int) -> str:
    path = Path(_cnf_path(nb_vars, ratio, seed))
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        generate_random_dimacs(str(path), nb_vars, round(nb_vars * ratio), seed=seed)
    return str(path)


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
