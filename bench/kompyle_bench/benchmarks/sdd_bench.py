# Copyright (c) 2026 Jaron Maene, Ibrahim El Kaddouri
# Licensed under apachev2
"""Reference WMC benchmark through pysdd's bottom-up evaluator."""

from __future__ import annotations

from array import array
from time import perf_counter

from kompyle_bench.weights import python_weights


def benchmark_pysdd(
    sdd,
    nb_vars: int,
    semiring: str,
    nb_repeats: int = 10,
    device: str = "cpu",
) -> dict:
    """Time ``wmc_manager.propagate()`` over ``nb_repeats`` runs.

    pysdd's ``propagate`` does both forward and backward in one call, so
    only a ``backward`` timing list is reported. Always CPU.
    """
    assert device == "cpu", "pysdd has no GPU backend"

    pos_weights, neg_weights = python_weights(nb_vars, semiring)
    # propagate() reads weights in the order [-n ... -1, +1 ... +n].
    pysdd_weights = array("d", neg_weights[::-1] + pos_weights)

    wmc = sdd.wmc(log_mode=(semiring == "log"))
    wmc.set_literal_weights_from_array(pysdd_weights)

    timings = []
    for _ in range(nb_repeats + 2):
        t1 = perf_counter()
        wmc.propagate()
        timings.append(perf_counter() - t1)
    return {"backward": timings[2:]}
