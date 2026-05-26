# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2
"""Per-backend inference benchmarks."""

from kompyle_bench.benchmarks.torch_bench import benchmark_klay_torch
from kompyle_bench.benchmarks.sdd_bench import benchmark_pysdd

__all__ = ["benchmark_klay_torch", "benchmark_pysdd"]
