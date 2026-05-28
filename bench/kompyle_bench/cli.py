# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2
"""command-line interface.

python -m kompyle_bench compile     <selector> --backend ... --exp-id ...
python -m kompyle_bench infer       <selector> --backend ... --semiring ... --device ...
python -m kompyle_bench experiment  <selector> --backend ... --semiring ... --device ...
python -m kompyle_bench serve       [--port 8080] [--exp-id N]

``<selector>`` is one of::

    --cnf PATH
    --nb-vars N --ratio R --seed S
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from kompyle_bench.backends import BACKENDS
from kompyle_bench.counters import COUNTERS
from kompyle_bench.instance import Instance, RealInstance, SyntheticInstance


WEB_DIR = Path(__file__).resolve().parent.parent / "web"
BENCHMARK_DIR = Path(__file__).resolve().parent.parent


def _instance_selector_parser() -> argparse.ArgumentParser:
    """Parent parser exposing the ``--cnf`` vs ``--nb-vars/--ratio/--seed`` selector."""
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument("--cnf",     default=None, metavar="PATH",
                   help="Path to a CNF file (real-instance mode).")
    p.add_argument("--nb-vars", type=int,   default=None, metavar="N",
                   help="Number of variables (synthetic mode).")
    p.add_argument("--ratio",   type=float, default=None, metavar="R",
                   help="Clause-to-variable ratio (synthetic mode).")
    p.add_argument("--seed",    type=int,   default=None, metavar="S",
                   help="RNG seed (synthetic mode).")
    return p


def _common_runner_parser() -> argparse.ArgumentParser:
    """Parent parser with flags every runner subcommand wants."""
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument("--exp-id", type=int, required=True, metavar="ID")
    return p


def _build_instance(args: argparse.Namespace) -> Instance:
    """Construct an `Instance` from CLI args, validating selectors."""
    if args.cnf is not None:
        if any(x is not None for x in (args.nb_vars, args.ratio, args.seed)):
            raise SystemExit("--cnf is mutually exclusive with synthetic flags")
        return RealInstance(path=Path(args.cnf))
    if None in (args.nb_vars, args.ratio, args.seed):
        raise SystemExit(
            "specify either --cnf, or all three of --nb-vars/--ratio/--seed"
        )
    return SyntheticInstance(
        nb_vars=args.nb_vars, ratio=args.ratio, seed=args.seed,
    )


# ----------------------------------------------------------------
# Subcommand handlers
# ----------------------------------------------------------------

def _cmd_compile(args: argparse.Namespace) -> int:
    from kompyle_bench.runners.compile import run_compile
    return run_compile(
        exp_id   = args.exp_id,
        instance = _build_instance(args),
        backend  = args.backend,
        timeout  = args.timeout,
        mem_mb   = args.mem_mb,
        out      = Path(args.out) if args.out else None,
    )


def _cmd_count(args: argparse.Namespace) -> int:
    from kompyle_bench.runners.count import run_count
    return run_count(
        exp_id   = args.exp_id,
        instance = _build_instance(args),
        mem_mb   = args.mem_mb,
        backend  = args.backend,
        timeout  = args.timeout,
        out      = Path(args.out) if args.out else None,
    )


def _cmd_infer(args: argparse.Namespace) -> int:
    from kompyle_bench.runners.infer import run_infer
    return run_infer(
        exp_id     = args.exp_id,
        instance   = _build_instance(args),
        backend    = args.backend,
        semiring   = args.semiring,
        device     = args.device,
        batch_size = args.batch_size,
        nb_repeats = args.nb_repeats,
    )


def _cmd_experiment(args: argparse.Namespace) -> int:
    from kompyle_bench.runners.experiment import run_experiment
    return run_experiment(
        exp_id   = args.exp_id,
        instance = _build_instance(args),
        backend  = args.backend,
        semiring = args.semiring,
        device   = args.device,
    )


def _cmd_serve(args: argparse.Namespace) -> int:
    from kompyle_bench.report.server import serve
    serve(
        benchmark_dir = Path(args.benchmark_dir).resolve(),
        web_dir       = Path(args.web_dir).resolve(),
        port          = args.port,
        exp           = args.exp,
    )
    return 0


# ----------------------------------------------------------------
# Top-level parser
# ----------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m kompyle_bench",
        description="Kompyle benchmark harness.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    inst = _instance_selector_parser()
    common = _common_runner_parser()

    # compile
    p_c = sub.add_parser(
        "compile",
        parents=[common, inst],
        help="Compile one instance with one backend.",
    )
    p_c.add_argument("--backend", required=True, choices=sorted(BACKENDS))
    p_c.add_argument("--timeout", type=int, default=300, metavar="SEC")
    p_c.add_argument("--mem-mb",  type=int, default=5000, metavar="MB")
    p_c.add_argument("--out",     default=None, metavar="PATH",
                     help="Override the output JSON path")
    p_c.set_defaults(func=_cmd_compile)

    # count
    p_co = sub.add_parser(
        "count",
        parents=[common, inst],
        help="Model-count without circuit construction "
             "(measure circuit-construction overhead vs the matching "
             "compile backend).",
    )
    p_co.add_argument("--backend", required=True, choices=sorted(COUNTERS))
    p_co.add_argument("--timeout", type=int, default=300, metavar="SEC")
    p_co.add_argument("--mem-mb",  type=int, default=5000, metavar="MB",
                      help="Forwarded to the matching backend option so the "
                           "count stage sees the same cache budget as compile.")
    p_co.add_argument("--out",     default=None, metavar="PATH",
                      help="Override the output JSON path")
    p_co.set_defaults(func=_cmd_count)

    # infer
    p_i = sub.add_parser(
        "infer",
        parents=[common, inst],
        help="Run inference benchmark for one parameter combination.",
    )
    p_i.add_argument("--backend",    required=True, choices=sorted(BACKENDS))
    p_i.add_argument("--semiring",   required=True, choices=["real", "log"])
    p_i.add_argument("--device",     default="cpu")
    p_i.add_argument("--batch-size", type=int, default=128)
    p_i.add_argument("--nb-repeats", type=int, default=10)
    p_i.set_defaults(func=_cmd_infer)

    # experiment
    p_e = sub.add_parser(
        "experiment",
        parents=[common, inst],
        help="Dummy-overhead structural analysis for one combination.",
    )
    p_e.add_argument("--backend",  required=True, choices=sorted(BACKENDS))
    p_e.add_argument("--semiring", required=True, choices=["real", "log"])
    p_e.add_argument("--device",   default="cpu")
    # nb-repeats / batch-size are reserved for re-adding profiled timings
    # (see analyze.py comment) without an interface change.
    p_e.add_argument("--nb-repeats", type=int, default=20)
    p_e.add_argument("--batch-size", type=int, default=32)
    p_e.set_defaults(func=_cmd_experiment)

    # serve
    p_s = sub.add_parser(
        "serve",
        help="Live dashboard server (auto-reloads result JSON on refresh).",
    )
    p_s.add_argument("--port",          type=int, default=8080)
    p_s.add_argument("--exp",           default=None, metavar="NAME",
                     help="Pin to one experiment name; default is latest on each request")
    p_s.add_argument("--benchmark-dir", default=str(BENCHMARK_DIR),
                     help="Where to find exps/ (default: package root)")
    p_s.add_argument("--web-dir",       default=str(WEB_DIR),
                     help="Where to find index.html + static/ (default: package root/web)")
    p_s.set_defaults(func=_cmd_serve)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
