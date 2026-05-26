# Copyright (c) 2026 Jaron Maene, Ibrahim El Kaddouri
# Licensed under apachev2
"""Random literal-weight generators for the inference benchmarks.

All weights are drawn uniformly from [0, 1]. In log semiring they are
transformed once with `numpy.log`. Negative-literal weights are
``1 - w`` (so that ``w + neg_w == 1`` in real semiring).
"""

from __future__ import annotations

import numpy as np


def numpy_weights(
    nb_vars: int,
    semiring: str,
    batch_size: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Generate ``(pos, neg)`` weight arrays of shape ``(batch_size, nb_vars)``."""
    weights = np.random.uniform(size=(batch_size, nb_vars)).astype(np.float32)
    neg_weights = 1 - weights
    if semiring == "log":
        weights = np.log(weights)
        neg_weights = np.log(neg_weights)
    return weights, neg_weights


def python_weights(
    nb_vars: int,
    semiring: str,
) -> tuple[list[float], list[float]]:
    """Single-sample variant returning plain Python lists (for pysdd)."""
    weights, neg_weights = numpy_weights(nb_vars, semiring, batch_size=1)
    return weights[0].tolist(), neg_weights[0].tolist()
