# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2
"""Result-file paths.

Every benchmark stage writes its results to a deterministic location
under ``exps/exp<NNNN>/results/<stage>/<sub>/<key>.json``.
"""

from __future__ import annotations

from pathlib import Path

from kompyle_bench.instance import Instance


def exp_root(exp_id: int) -> Path:
    return Path(f"exps/exp{exp_id:04d}")


def compile_result_path(exp_id: int, instance: Instance, backend: str) -> Path:
    return (
        exp_root(exp_id)
        / "results" / "compile" / backend
        / f"{instance.key}.json"
    )


def count_result_path(exp_id: int, instance: Instance, backend: str) -> Path:
    return (
        exp_root(exp_id)
        / "results" / "count" / backend
        / f"{instance.key}.json"
    )


def infer_result_path(
    exp_id: int,
    instance: Instance,
    backend: str,
    semiring: str,
    device: str,
) -> Path:
    return (
        exp_root(exp_id)
        / "results" / "infer" / f"{backend}_{semiring}_{device}"
        / f"{instance.key}.json"
    )


def experiment_result_path(
    exp_id: int,
    instance: Instance,
    backend: str,
    semiring: str,
    device: str,
) -> Path:
    return (
        exp_root(exp_id)
        / "results" / "experiment" / "dummy_overhead"
        / f"{backend}_{semiring}_{device}"
        / f"{instance.key}.json"
    )
