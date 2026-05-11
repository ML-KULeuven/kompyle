#!/usr/bin/env python3
# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2
import argparse
import sys

from analysis import run_one_experiment, run_one_experiment_cnf


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Dummy-node overhead experiment for one parameter combination."
    )

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--cnf",      default=None, metavar="PATH",
                      help="Direct path to a CNF file (real-instance mode).")
    mode.add_argument("--nb-vars",  type=int,     default=None, metavar="N",
                      help="Number of variables (synthetic mode).")

    parser.add_argument("--ratio",      type=float, default=None, metavar="R")
    parser.add_argument("--seed",       type=int,   default=None, metavar="S")
    parser.add_argument("--backend",    required=True,
                        choices=["ganak", "ganak_arjun", "d4v2", "sdd"])
    parser.add_argument("--semiring",   required=True, choices=["real", "log"])
    parser.add_argument("--device",     default="cpu")
    parser.add_argument("--nb-repeats", type=int,   default=20)
    parser.add_argument("--batch-size", type=int,   default=32)
    parser.add_argument("--exp-id",     type=int,   required=True, metavar="ID")
    parser.add_argument("--collapse",   type=int,   choices=[0, 1], default=0)
    parser.add_argument("--merge",      type=int,   choices=[0, 1], default=0)
    args = parser.parse_args()

    if args.cnf is not None:
        return run_one_experiment_cnf(
            exp_id     = args.exp_id,
            cnf_path   = args.cnf,
            backend    = args.backend,
            semiring   = args.semiring,
            dev        = args.device,
            nb_repeats = args.nb_repeats,
            batch_size = args.batch_size,
            collapse   = args.collapse,
            merge      = args.merge,
        )
    else:
        if args.ratio is None or args.seed is None:
            parser.error("--ratio and --seed are required in synthetic mode.")
        return run_one_experiment(
            exp_id     = args.exp_id,
            nb_vars    = args.nb_vars,
            ratio      = args.ratio,
            seed       = args.seed,
            backend    = args.backend,
            semiring   = args.semiring,
            dev        = args.device,
            nb_repeats = args.nb_repeats,
            batch_size = args.batch_size,
            collapse   = args.collapse,
            merge      = args.merge,
        )


if __name__ == "__main__":
    sys.exit(main())
