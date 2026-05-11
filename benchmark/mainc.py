#!/usr/bin/env python3
# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2
import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from compilation    import compile_one
from util           import (
    compile_result_path,
    _ensure_cnf,
    exp_root
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compile one CNF instance with one backend."
    )
    parser.add_argument("--nb-vars",  type=int,   default=None,   metavar="N")
    parser.add_argument("--ratio",    type=float, default=None,   metavar="R")
    parser.add_argument("--seed",     type=int,   default=None,   metavar="S")
    parser.add_argument("--cnf",      default=None, metavar="PATH",
                        help="Direct path to a CNF file (skips random generation).")
    parser.add_argument("--backend",  required=True,
                        choices=["ganak", "ganak_arjun", "d4v2", "sdd", "isymganak"])
    parser.add_argument("--timeout",  type=int,   default=300,    metavar="SEC")
    parser.add_argument("--mem-mb",   type=int,   default=5000,   metavar="MB")
    parser.add_argument("--dot",      default=None, metavar="DIR",
                        help="Export circuit .dot/.svg files to this directory")
    parser.add_argument("--out",      default=None, metavar="PATH",
                        help="Override the output JSON path")
    parser.add_argument("--exp-id",   type=int,   required=True,  metavar="ID")
    args = parser.parse_args()

    if args.cnf is not None:
        cnf  = args.cnf
        stem = Path(cnf).stem
        out  = (
            Path(args.out)
            if args.out
            else (
                exp_root(args.exp_id)
                / "results" / "compile" / args.backend
                / f"{stem}.json"
            )
        )
    else:
        if args.nb_vars is None or args.ratio is None or args.seed is None:
            parser.error("--nb-vars, --ratio, and --seed are required unless --cnf is given.")
        cnf = _ensure_cnf(args.nb_vars, args.ratio, args.seed)
        out = (
            Path(args.out)
            if args.out
            else compile_result_path(
                args.exp_id, args.nb_vars, args.ratio, args.seed, args.backend
            )
        )

    if out.exists():
        print(f"[skip] {out}")
        return 0

    result = compile_one(cnf,
                         args.backend,
                         timeout=args.timeout,
                         mem_mb=args.mem_mb,
                         dot_dir=args.dot)

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(asdict(result), indent=2))

    tag = (
        "TIMEOUT" if result.timed_out
        else f"ERROR: {result.error}" if result.error
        else f"OK  {result.compile_s:.2f}s / {result.circuit_nodes}n"
    )
    if args.cnf is not None:
        label = f"{args.backend:15s}  cnf={Path(args.cnf).name:40s}  →  {tag}"
    else:
        label = (
            f"{args.backend:15s}  v={args.nb_vars:3d}  r={args.ratio:.1f}"
            f"  s={args.seed}  →  {tag}"
        )
    print(label)
    return 0


if __name__ == "__main__":
    sys.exit(main())
