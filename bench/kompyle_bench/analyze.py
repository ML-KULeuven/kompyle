# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2
"""Structural analysis of a compiled circuit.

The "dummy overhead" experiment counts how many *relay* layers a
compiled circuit has. Layers in which every output has exactly one
incoming edge, so the scatter-reduce degenerates to a gather. These
layers contribute index-buffer memory and dispatch overhead without
doing any real work.
"""

from __future__ import annotations

from typing import Any

import torch


def _is_relay_layer(ix_in: torch.Tensor, ix_out: torch.Tensor) -> bool:
    """One incoming edge per output ⇒ relay layer."""
    n_edges = ix_in.shape[0]
    n_outputs = int(ix_out[-1].item()) + 1
    return n_edges == n_outputs


def analyze_circuit_module(circuit_module) -> dict[str, Any]:
    """Walk all layers and return aggregate + per-layer relay stats.

    Each ix_in / ix_out is int64 (8 bytes per element). Index buffer
    accounting reports separately how many bytes are spent on relay vs
    genuine layers.
    """
    BYTES_PER_INT64 = 8

    relay_layers = 0
    dummy_edges = 0
    real_edges = 0
    bytes_dummy = 0
    bytes_real = 0
    per_layer = []

    for i, layer in enumerate(circuit_module.layers):
        n_edges = layer.ix_in.shape[0]
        relay = _is_relay_layer(layer.ix_in, layer.ix_out)
        buf_bytes = (layer.ix_in.numel() + layer.ix_out.numel()) * BYTES_PER_INT64

        if relay:
            relay_layers += 1
            dummy_edges += n_edges
            bytes_dummy += buf_bytes
        else:
            real_edges += n_edges
            bytes_real += buf_bytes

        per_layer.append({
            "layer_idx": i,
            "n_edges":   n_edges,
            "n_outputs": int(layer.ix_out[-1].item()) + 1,
            "relay":     relay,
            "buf_bytes": buf_bytes,
        })

    total_layers = len(circuit_module.layers)
    total_edges = dummy_edges + real_edges
    total_bytes = bytes_dummy + bytes_real

    return {
        "relay_layers":        relay_layers,
        "total_layers":        total_layers,
        "relay_fraction":      relay_layers / total_layers if total_layers else 0.0,
        "dummy_edges":         dummy_edges,
        "real_edges":          real_edges,
        "total_edges":         total_edges,
        "dummy_edge_fraction": dummy_edges / total_edges if total_edges else 0.0,
        "index_bytes_total":   total_bytes,
        "index_bytes_dummy":   bytes_dummy,
        "index_bytes_real":    bytes_real,
        "per_layer":           per_layer,
    }
