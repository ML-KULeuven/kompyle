#!/usr/bin/env python3
# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2
import argparse
import json
import sys
from pathlib import Path

from pysdd.sdd import SddManager

import kompyle as p

from btorch         import benchmark_klay_torch
from bsdd           import benchmark_pysdd
from util           import (
    _silence_fd,
    _restore_fd,
    compile_result_path,
    compile_result_path_cnf,
    infer_result_path,
    infer_result_path_cnf,
    _cnf_path,
    read_nb_vars_from_cnf,
    parse_cnf,
    FormulaCircuitPair,
    assert_exhaustive_equivalence,
)

VERIFY_MAX_VARS = 30
VERIFY_MAX_CLS  = 75


def _recompile(cnf: str, backend: str):
    """
    Recompile the circuit in the current process.
    Returns (circuit, sdd_pair) where sdd_pair is (mgr, sdd) for the sdd
    backend and None otherwise.
    """
    circuit = p.Circuit()
    devnull, old_out, old_err = _silence_fd()

    if backend == "ganak":
        root = p.compile_from_cnf_using_ganak(circuit, cnf, arjun_options=None)
    elif backend == "ganak_arjun":
        root = p.compile_from_cnf_using_ganak(circuit, cnf, arjun_options=p.ArjunOptions())
    elif backend == "d4v2":
        root = p.compile_from_cnf_using_d4v2(circuit, cnf)
    elif backend == "sdd":
        mgr, sdd = SddManager.from_cnf_file(cnf.encode(), vtree_type=b"balanced")
        root = p.compile_from_sdd(circuit, sdd)
        _restore_fd(devnull, old_out, old_err)
        assert root is not None
        circuit.set_root(root)
        return circuit, (mgr, sdd)
    else:
        _restore_fd(devnull, old_out, old_err)
        raise ValueError(f"Unknown backend: {backend}")

    _restore_fd(devnull, old_out, old_err)
    assert root is not None
    circuit.set_root(root)
    return circuit, None


def run_one_infer(
    exp_id:     int,
    nb_vars:    int,
    ratio:      float,
    seed:       int,
    backend:    str,
    semiring:   str,
    device:     str,
    collapse:   bool = False,
    merge:      bool = False,
    batch_size: int  = 128,
    nb_repeats: int  = 10,
    verify:     bool = True,
) -> int:
    """
    Run the infer benchmark for a single synthetic (nb_vars, ratio, seed) set.
    Returns 0 on success-or-skip, 1 on error.
    """
    cp = compile_result_path(exp_id, nb_vars, ratio, seed, backend)
    if not cp.exists():
        print(f"[skip] no compile result: {cp}")
        return 1

    cr = json.loads(cp.read_text())
    if cr.get("compile_s") is None:
        print(f"[skip] compile timed-out or errored: {cp}")
        return 0

    out = infer_result_path(exp_id, nb_vars, ratio, seed, backend, semiring, device)
    if out.exists():
        print(f"[skip] {out}")
        return 0

    cnf = str(_cnf_path(nb_vars, ratio, seed))
    circuit, sdd_pair = _recompile(cnf, backend)

    if verify and nb_vars <= VERIFY_MAX_VARS and (nb_vars * ratio) <= VERIFY_MAX_CLS:
        n_vars, clauses = parse_cnf(cnf)
        pair = FormulaCircuitPair(
            path=cnf, n_vars=n_vars, circuit=circuit, root=circuit,
            desc=f"{backend}[verify]", compiler_id=backend, _clauses=clauses,
        )
        try:
            assert_exhaustive_equivalence(pair)
            print(f"[verify] OK  {backend}  v={nb_vars}  r={ratio:.1f}  s={seed}")
        except AssertionError as e:
            print(f"[verify] FAIL  {e}")
            return 1

    results: dict = {"circuit_nodes": cr["circuit_nodes"]}
    results.update(
        benchmark_klay_torch(
            circuit, nb_vars, semiring,
            nb_repeats=nb_repeats, device=device,
            batch_size=batch_size, collapse=collapse, merge=merge,
        )
    )
    if sdd_pair is not None:
        mgr, sdd = sdd_pair
        results["pysdd"] = benchmark_pysdd(sdd, nb_vars, semiring)

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, indent=2))
    print(
        f"OK  {backend:15s}  {semiring:4s}  v={nb_vars}  r={ratio:.1f}"
        f"  s={seed}  device={device}"
    )
    return 0


def run_one_infer_cnf(
    exp_id:     int,
    cnf_path:   str,
    backend:    str,
    semiring:   str,
    device:     str,
    collapse:   bool = False,
    merge:      bool = False,
    batch_size: int  = 128,
    nb_repeats: int  = 10,
) -> int:
    """
    Run the infer benchmark for a real (non-synthetic) CNF instance.
    Result paths are keyed by the CNF file stem.
    Returns 0 on success-or-skip, 1 on error.
    """
    stem = Path(cnf_path).stem

    cp = compile_result_path_cnf(exp_id, stem, backend)
    if not cp.exists():
        print(f"[skip] no compile result: {cp}")
        return 1

    cr = json.loads(cp.read_text())
    if cr.get("compile_s") is None:
        print(f"[skip] compile timed-out or errored: {cp}")
        return 0

    out = infer_result_path_cnf(exp_id, stem, backend, semiring, device)
    if out.exists():
        print(f"[skip] {out}")
        return 0

    # nb_vars is needed for weight generation — read it from the CNF header.
    nb_vars = read_nb_vars_from_cnf(cnf_path)

    circuit, sdd_pair = _recompile(cnf_path, backend)

    results: dict = {"circuit_nodes": cr["circuit_nodes"]}
    results.update(
        benchmark_klay_torch(
            circuit, nb_vars, semiring,
            nb_repeats=nb_repeats, device=device,
            batch_size=batch_size, collapse=collapse, merge=merge,
        )
    )
    if sdd_pair is not None:
        mgr, sdd = sdd_pair
        results["pysdd"] = benchmark_pysdd(sdd, nb_vars, semiring)

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, indent=2))
    print(
        f"OK  {backend:15s}  {semiring:4s}"
        f"  cnf={Path(cnf_path).name:40s}  device={device}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Inference benchmark for one parameter combination."
    )

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--cnf",      default=None, metavar="PATH",
                      help="Direct path to a CNF file (real-instance mode).")
    mode.add_argument("--nb-vars",  type=int,     default=None, metavar="N",
                      help="Number of variables (synthetic mode).")

    parser.add_argument("--ratio",      type=float, default=None,  metavar="R")
    parser.add_argument("--seed",       type=int,   default=None,  metavar="S")
    parser.add_argument("--backend",    required=True,
                        choices=["ganak", "ganak_arjun", "d4v2", "sdd"])
    parser.add_argument("--semiring",   required=True, choices=["real", "log"])
    parser.add_argument("--device",     default="cpu")
    parser.add_argument("--batch-size", type=int,   default=128)
    parser.add_argument("--nb-repeats", type=int,   default=10)
    parser.add_argument("--exp-id",     type=int,   required=True, metavar="ID")
    parser.add_argument("--collapse",   type=int,   choices=[0, 1], default=0)
    parser.add_argument("--merge",      type=int,   choices=[0, 1], default=0)
    parser.add_argument("--no-verify",  action="store_true",
                        help="skip exhaustive equivalence check")
    parser.add_argument("--verify",     type=int,   choices=[0, 1], default=0)
    args = parser.parse_args()

    if args.cnf is not None:
        return run_one_infer_cnf(
            exp_id     = args.exp_id,
            cnf_path   = args.cnf,
            backend    = args.backend,
            semiring   = args.semiring,
            device     = args.device,
            batch_size = args.batch_size,
            nb_repeats = args.nb_repeats,
            collapse   = args.collapse,
            merge      = args.merge,
        )
    else:
        if args.ratio is None or args.seed is None:
            parser.error("--ratio and --seed are required in synthetic mode.")
        return run_one_infer(
            exp_id     = args.exp_id,
            nb_vars    = args.nb_vars,
            ratio      = args.ratio,
            seed       = args.seed,
            backend    = args.backend,
            semiring   = args.semiring,
            device     = args.device,
            batch_size = args.batch_size,
            nb_repeats = args.nb_repeats,
            collapse   = args.collapse,
            merge      = args.merge,
            verify     = args.verify,
        )


if __name__ == "__main__":
    sys.exit(main())
