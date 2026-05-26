#!/usr/bin/env bash
# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2
#
# Sweep grid
# the single source of truth for what (nb_vars, ratio, seed,
# backend, semiring, device) combinations every script should explore.
#
# Both the local GNU-parallel scripts and the SLURM array scripts source
# this file.

# ---------------------------------------------------------
# compile / infer grid (synthetic)
# ---------------------------------------------------------

readonly -a NB_VARS=(30 35 40 45 50 55 60 65 70 75 80)
readonly -a RATIOS=(2.5 3.0 3.5 4.0 4.5 5.0)
readonly -a SEEDS=(0 1 2 3)
readonly -a BACKENDS=(ganak ganak_arjun d4v2 sdd)
readonly -a COUNT_BACKENDS=(
    ganak_count ganak_arjun_count ganak_arjun_wmc_count d4v2_count sdd_count
    ganak_bin_count ganak_arjun_bin_count d4v2_bin_count isymganak_bin_count
)

# ---------------------------------------------------------
# infer-only knobs
# ---------------------------------------------------------

readonly -a SEMIRINGS=(real log)
readonly -a DEVICES=(cpu cuda)

# ---------------------------------------------------------
# per-run defaults (override by exporting before sourcing)
# ---------------------------------------------------------

: "${BATCH:=32}"
: "${NB_REPEATS:=10}"
: "${VERIFY:=0}"

# ---------------------------------------------------------
# helpers
# ---------------------------------------------------------

synth_n_compile_tasks() {
    echo $(( ${#NB_VARS[@]} * ${#RATIOS[@]} * ${#SEEDS[@]} * ${#BACKENDS[@]} ))
}

synth_n_count_tasks() {
    echo $(( ${#NB_VARS[@]} * ${#RATIOS[@]} * ${#SEEDS[@]} * ${#COUNT_BACKENDS[@]} ))
}
