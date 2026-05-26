# Copyright (c) 2026 Jaron Maene, Ibrahim El Kaddouri
# Licensed under apachev2
"""Timing the klay-compiled circuit through PyTorch.

Three timings are reported:
* ``to_torch``  one-shot cost of converting the kompyle circuit to a torch ``Module``.
* ``jit compile``  one-shot cost of ``torch.compile`` on the vmapped module.
* ``forward (warm)``  list of ``nb_repeats`` forward-pass wall times.
* ``+backward (warm)``  same, but each iteration also runs ``.mean().backward()``.

Two warmup iterations are discarded before measurement, both for the
forward-only loop and the forward+backward loop.
"""

from __future__ import annotations

from time import perf_counter

import torch
from pysdd.iterator import SddIterator

from kompyle_bench.weights import numpy_weights


def _torch_weights(nb_vars: int, semiring: str, device: str, batch_size: int):
    weights, neg_weights = numpy_weights(nb_vars, semiring, batch_size)
    weights = torch.as_tensor(weights).to(device)
    neg_weights = torch.as_tensor(neg_weights).to(device)
    weights.requires_grad = True
    neg_weights.requires_grad = True
    return weights, neg_weights


def benchmark_klay_torch(
    circuit,
    nb_vars: int,
    semiring: str,
    nb_repeats: int = 10,
    device: str = "cpu",
    batch_size: int | None = None,
) -> dict:
    """Time the klay-compiled circuit through PyTorch.

    ``batch_size`` is required, we vmap over the batch dimension.
    """
    assert batch_size is not None, "batch_size is required"
    results: dict = {}

    t1 = perf_counter()
    fwd = circuit.to_torch_module(semiring)
    fwd.to(device)
    results["to_torch"] = perf_counter() - t1
    results["sparsity"] = fwd.sparsity(nb_vars)

    fwd = torch.vmap(fwd)

    t1 = perf_counter()
    fwd = torch.compile(fwd, mode="reduce-overhead")
    results["jit compile"] = perf_counter() - t1

    # forward-only loop (2 warmup + nb_repeats)
    timings_fwd = []
    with torch.no_grad():
        for _ in range(nb_repeats + 2):
            w, nw = _torch_weights(nb_vars, semiring, device, batch_size)
            t1 = perf_counter()
            fwd(w, nw)
            if device == "cuda":
                torch.cuda.synchronize()
            timings_fwd.append(perf_counter() - t1)
    results["forward (cold)"] = timings_fwd[0]
    results["forward (warm)"] = timings_fwd[2:]

    # forward + backward loop (2 warmup + nb_repeats)
    timings_bwd = []
    for _ in range(nb_repeats + 2):
        w, nw = _torch_weights(nb_vars, semiring, device, batch_size)
        t1 = perf_counter()
        fwd(w, nw).mean().backward()
        if device == "cuda":
            torch.cuda.synchronize()
        timings_bwd.append(perf_counter() - t1)
    results[" +backward (cold)"] = timings_bwd[0]
    results[" +backward (warm)"] = timings_bwd[2:]
    return results
