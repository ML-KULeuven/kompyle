#!/usr/bin/env python3
# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2
import argparse
import sys

from analysis import run_one_experiment


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Dummy-node overhead experiment for one parameter combination."
    )
    parser.add_argument("--nb-vars",    type=int,   required=True,  metavar="N")
    parser.add_argument("--ratio",      type=float, required=True,  metavar="R")
    parser.add_argument("--seed",       type=int,   required=True,  metavar="S")
    parser.add_argument("--backend",    required=True,
                        choices=["ganak", "ganak_arjun", "d4v2", "sdd"])
    parser.add_argument("--semiring",   required=True, choices=["real", "log"])
    parser.add_argument("--device",     default="cpu")
    parser.add_argument("--nb-repeats", type=int,   default=20)
    parser.add_argument("--batch-size", type=int,   default=32)
    parser.add_argument("--exp-id",     type=int,   required=True,  metavar="ID")
    args = parser.parse_args()

    return run_one_experiment(
        exp_id      = args.exp_id,
        nb_vars     = args.nb_vars,
        ratio       = args.ratio,
        seed        = args.seed,
        backend     = args.backend,
        semiring    = args.semiring,
        device      = args.device,
        nb_repeats  = args.nb_repeats,
        batch_size  = args.batch_size,
    )


if __name__ == "__main__":
    sys.exit(main())
