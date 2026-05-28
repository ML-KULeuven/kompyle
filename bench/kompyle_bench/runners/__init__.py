# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2
"""Per-stage runners.

Each runner takes a single `~kompyle_bench.instance.Instance` and
a parameter set, runs the relevant work, and writes a result JSON
to disk under ``exps/exp<NNNN>/results/...``. The CLI module is what
actually parses argv and invokes these.
"""
