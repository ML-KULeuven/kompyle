#!/usr/bin/env bash
# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2
#
# Local synthetic-sweep driver (workstation, not HPC).
# Runs the full grid through GNU parallel.
#
# Usage:
#   bash scripts/local/sweep_synth.sh <exp_id> [phase] [-- extra parallel opts]
#
# Phases: compile | infer | experiment | all (default: all)
#
# Example:
#   bash scripts/local/sweep_synth.sh 7 compile -- --jobs 8

set -euo pipefail

# --- resolve locations -----------------------------------------------------
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${script_dir}/../lib/common.sh"
source "${script_dir}/../lib/grid.sh"

EXP_ID="${1:?Usage: $0 <exp_id> [phase]}"
PHASE="${2:-all}"
shift 2 2>/dev/null || shift $#

# Memory / timeout knobs
: "${MEM_MB:=5000}"
: "${TIMEOUT:=300}"
: "${COUNT_TIMEOUT:=300}"

PARALLEL_OPTS=(
    --eta
    --line-buffer
    --jobs 4
    # --halt now,fail=1
    # --memfree 10G
    # --noswap
    "$@"
)

cd "${benchmark_dir}"

# ---------------------------------------------------
# phases
# ---------------------------------------------------


py() {
    python -m kompyle_bench "$@"
}

run_compile() {
    log "=== compile phase ==="
    parallel "${PARALLEL_OPTS[@]}"          \
        python -m kompyle_bench compile     \
            --nb-vars {1}                   \
            --ratio   {2}                   \
            --seed    {3}                   \
            --backend {4}                   \
            --exp-id  "${EXP_ID}"           \
            --timeout "${TIMEOUT}"          \
            --mem-mb  "${MEM_MB}"           \
    ::: "${NB_VARS[@]}"                     \
    ::: "${RATIOS[@]}"                      \
    ::: "${SEEDS[@]}"                       \
    ::: "${BACKENDS[@]}"
}

run_count() {
    log "=== count phase ==="
    parallel "${PARALLEL_OPTS[@]}"            \
        python -m kompyle_bench count         \
            --nb-vars {1}                     \
            --ratio   {2}                     \
            --seed    {3}                     \
            --backend {4}                     \
            --exp-id  "${EXP_ID}"             \
            --timeout "${COUNT_TIMEOUT}"      \
            --mem-mb  "${MEM_MB}"             \
    ::: "${NB_VARS[@]}"                       \
    ::: "${RATIOS[@]}"                        \
    ::: "${SEEDS[@]}"                         \
    ::: "${COUNT_BACKENDS[@]}"
}

run_infer() {
    log "=== infer phase ==="
    parallel "${PARALLEL_OPTS[@]}"          \
        python -m kompyle_bench infer       \
            --nb-vars     {1}               \
            --ratio       {2}               \
            --seed        {3}               \
            --backend     {4}               \
            --semiring    {5}               \
            --device      {6}               \
            --batch-size  "${BATCH}"        \
            --nb-repeats  "${NB_REPEATS}"   \
            --exp-id      "${EXP_ID}"       \
            --verify      "${VERIFY}"       \
    ::: "${NB_VARS[@]}"                     \
    ::: "${RATIOS[@]}"                      \
    ::: "${SEEDS[@]}"                       \
    ::: "${BACKENDS[@]}"                    \
    ::: "${SEMIRINGS[@]}"                   \
    ::: "${DEVICES[@]}"
}

run_experiment() {
    log "=== experiment phase ==="
    parallel "${PARALLEL_OPTS[@]}"          \
        python -m kompyle_bench experiment  \
            --nb-vars     {1}               \
            --ratio       {2}               \
            --seed        {3}               \
            --backend     {4}               \
            --semiring    "${SEMIRINGS[0]}" \
            --device      "${DEVICES[0]}"   \
            --nb-repeats  "${NB_REPEATS}"   \
            --batch-size  "${BATCH}"        \
            --exp-id      "${EXP_ID}"       \
    ::: "${NB_VARS[@]}"                     \
    ::: "${RATIOS[@]}"                      \
    ::: "${SEEDS[@]}"                       \
    ::: "${BACKENDS[@]}"
}

case "${PHASE}" in
    compile)    run_compile    ;;
    count)      run_count      ;;
    infer)      run_infer      ;;
    experiment) run_experiment ;;
    all)
        run_compile
        run_count
        run_infer
        run_experiment
        ;;
    *) die "unknown phase: ${PHASE} \
            (valid: compile | count | infer | experiment | all)" ;;
esac

log "=== done ==="
