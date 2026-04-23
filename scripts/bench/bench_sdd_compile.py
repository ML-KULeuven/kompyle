#!/usr/bin/env python3
"""Benchmark compile_from_sdd_cpp vs compile_from_sdd_py."""

from __future__ import annotations

import argparse
import gc
import statistics as stats
import time
from dataclasses import dataclass
from typing import Callable, Iterable, List

from pysdd.sdd import SddManager
from kompyle import Circuit, compile_from_sdd_cpp, compile_from_sdd_py

from tqdm import tqdm
import random


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


def write_dimacs(path: str, clauses: List[List[int]], n_vars: int):
    with open(path, "w") as f:
        f.write(f"p cnf {n_vars} {len(clauses)}\n")

        for clause in clauses:
            f.write(" ".join(map(str, clause)) + " 0\n")

@dataclass(frozen=True)
class BenchResult:
    size: int
    func_name: str
    mean_ns: float
    median_ns: float
    min_ns: float
    max_ns: float


# ---------------------------
# SDD builder
# ---------------------------
def build_sample_sdd(n: int, m: int, seed: int):
    clauses_raw = random_clauses(n, m, k=3, seed=seed)

    manager = SddManager(var_count=n)

    def lit(v: int):
        var = abs(v)
        node = manager.literal(var)
        return node if v > 0 else ~node

    clause_nodes = []
    for clause in clauses_raw:
        acc = lit(clause[0])
        for v in clause[1:]:
            acc = acc | lit(v)
        clause_nodes.append(acc)

    node = clause_nodes[0]
    for clause in clause_nodes[1:]:
        node = node & clause

    return manager, node


# ---------------------------
# Timing
# ---------------------------
def time_function(
    func: Callable[[object, object], object],
    node: object,
    *,
    number: int,
    repeat: int,
) -> tuple[float, float, float, float]:
    """Returns (mean_ns, median_ns, min_ns, max_ns) per call."""

    was_enabled = gc.isenabled()
    gc.disable()

    try:
        # warmup
        circuit = Circuit()
        func(circuit, node)

        samples = []
        last_result = None

        for _ in range(repeat):
            t0 = time.perf_counter_ns()

            for _ in range(number):
                circuit = Circuit()
                last_result = func(circuit, node)

            elapsed = time.perf_counter_ns() - t0
            samples.append(elapsed / number)

        _ = last_result

        return (
            stats.mean(samples),
            stats.median(samples),
            min(samples),
            max(samples),
        )

    finally:
        if was_enabled:
            gc.enable()


# ---------------------------
# Benchmark runner
# ---------------------------
def run_benchmark(
    configs: Iterable[tuple[int, int, int]],
    *,
    number: int,
    repeat: int,
) -> list[BenchResult]:

    results: list[BenchResult] = []

    configs = list(configs)

    for n, m, seed in tqdm(configs, desc="SDD configs"):
        manager, node = build_sample_sdd(n, m, seed)
        _ = manager

        funcs = [compile_from_sdd_cpp, compile_from_sdd_py]

        for func in tqdm(funcs, desc=f"n={n}", leave=False):
            mean_ns, median_ns, min_ns, max_ns = time_function(
                func,
                node,
                number=number,
                repeat=repeat,
            )

            results.append(
                BenchResult(
                    size=n,
                    func_name=func.__name__,
                    mean_ns=mean_ns,
                    median_ns=median_ns,
                    min_ns=min_ns,
                    max_ns=max_ns,
                )
            )

    return results


# ---------------------------
# Output
# ---------------------------
def print_results(results: list[BenchResult]) -> None:
    print(
        f"{'vars':>6}  {'function':<22}  "
        f"{'mean (µs)':>12}  {'mean (s)':>10}  "
        f"{'median (µs)':>12}  {'median (s)':>10}  "
        f"{'min (µs)':>10}  {'min (s)':>10}  "
        f"{'max (µs)':>10}  {'max (s)':>10}"
    )
    print("-" * 120)

    for r in results:
        mean_s = r.mean_ns / 1_000_000_000
        median_s = r.median_ns / 1_000_000_000
        min_s = r.min_ns / 1_000_000_000
        max_s = r.max_ns / 1_000_000_000

        print(
            f"{r.size:6d}  {r.func_name:<22}  "
            f"{r.mean_ns / 1_000:12.3f}  {mean_s:10.6f}  "
            f"{r.median_ns / 1_000:12.3f}  {median_s:10.6f}  "
            f"{r.min_ns / 1_000:10.3f}  {min_s:10.6f}  "
            f"{r.max_ns / 1_000:10.3f}  {max_s:10.6f}"
        )

# ---------------------------
# Main
# ---------------------------
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--number", type=int, default=1)
    parser.add_argument("--repeat", type=int, default=1)
    args = parser.parse_args()

    configs = [
        (6, 18, 7),
        (6, 18, 42),
        (6, 18, 1337),
        (12, 36, 17),
        (12, 36, 142),
        (12, 36, 337),
        (25, 75, 12),
        (25, 75, 3232),
        (25, 75, 1232),
        (50, 150, 32),
        (50, 150, 123),
        (50, 150, 14311),
        # (60, 180, 0),
        # (75, 225, 0),
        # (150, 450, 0),
    ]

    results = run_benchmark(configs, number=args.number, repeat=args.repeat)
    print_results(results)



if __name__ == "__main__":
    main()
