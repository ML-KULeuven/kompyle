#!/usr/bin/env bash
# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2
#
# Local real-instance sweep driver
# Iterates the problems listed in assets/all_problems.txt
#
# Usage:
#   bash scripts/local/sweep_real.sh <exp_id> [phase] [-- extra parallel opts]

set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${script_dir}/../lib/common.sh"
source "${script_dir}/../lib/grid.sh"

EXP_ID="${1:?Usage: $0 <exp_id> [phase]}"
PHASE="${2:-all}"
shift 2 2>/dev/null || shift $#

INSTANCES_DIR="${INSTANCES_DIR:-${benchmark_dir}/assets}"
PROBLEMS_FILE="${PROBLEMS_FILE:-${benchmark_dir}/assets/all_problems.txt}"
require_file "${PROBLEMS_FILE}"

mapfile -t PROBLEMS < "${PROBLEMS_FILE}"
log "Problems: ${#PROBLEMS[@]}  Backends: ${#BACKENDS[@]}"
log "Total compile tasks: $(( ${#PROBLEMS[@]} * ${#BACKENDS[@]} ))"

: "${MEM_MB:=5000}"
: "${TIMEOUT:=300}"

PARALLEL_OPTS=(
    --eta
    --line-buffer
    --jobs 4
    "$@"
)

cd "${benchmark_dir}"

# ---------------------------------------------------
# helpers
# ---------------------------------------------------

emit_compile_pairs() {
    for problem in "${PROBLEMS[@]}"; do
        local cnf="${INSTANCES_DIR}/${problem}"
        if [[ ! -f "${cnf}" ]]; then
            echo "WARN: missing instance, skipping: ${cnf}" >&2
            continue
        fi
        for backend in "${BACKENDS[@]}"; do
            printf '%s:::%s\n' "${cnf}" "${backend}"
        done
    done
}

emit_count_pairs() {
    for problem in "${PROBLEMS[@]}"; do
        local cnf="${INSTANCES_DIR}/${problem}"
        [[ -f "${cnf}" ]] || continue
        for backend in "${COUNT_BACKENDS[@]}"; do
            printf '%s:::%s\n' "${cnf}" "${backend}"
        done
    done
}

emit_infer_pairs() {
    for problem in "${PROBLEMS[@]}"; do
        local cnf="${INSTANCES_DIR}/${problem}"
        [[ -f "${cnf}" ]] || continue
        for backend in "${BACKENDS[@]}"; do
            for sr in "${SEMIRINGS[@]}"; do
                for dev in "${DEVICES[@]}"; do
                    printf '%s:::%s:::%s:::%s\n' "${cnf}" "${backend}" "${sr}" "${dev}"
                done
            done
        done
    done
}

emit_experiment_pairs() {
    for problem in "${PROBLEMS[@]}"; do
        local cnf="${INSTANCES_DIR}/${problem}"
        [[ -f "${cnf}" ]] || continue
        for backend in "${BACKENDS[@]}"; do
            printf '%s:::%s\n' "${cnf}" "${backend}"
        done
    done
}

# ---------------------------------------------------
# phases
# ---------------------------------------------------

run_compile() {
    log "=== compile phase ==="
    emit_compile_pairs | \
    parallel "${PARALLEL_OPTS[@]}" --colsep ':::'  \
        python -m kompyle_bench compile            \
            --cnf     {1}                          \
            --backend {2}                          \
            --exp-id  "${EXP_ID}"                  \
            --timeout "${TIMEOUT}"                 \
            --mem-mb  "${MEM_MB}"
}

run_count() {
    log "=== count phase ==="
    emit_count_pairs | \
    parallel "${PARALLEL_OPTS[@]}" --colsep ':::'  \
        python -m kompyle_bench count              \
            --cnf     {1}                          \
            --backend {2}                          \
            --exp-id  "${EXP_ID}"                  \
            --timeout "${TIMEOUT}"                 \
            --mem-mb  "${MEM_MB}"
}

run_infer() {
    log "=== infer phase ==="
    emit_infer_pairs | \
    parallel "${PARALLEL_OPTS[@]}" --colsep ':::'  \
        python -m kompyle_bench infer              \
            --cnf         {1}                      \
            --backend     {2}                      \
            --semiring    {3}                      \
            --device      {4}                      \
            --batch-size  "${BATCH}"               \
            --nb-repeats  "${NB_REPEATS}"          \
            --exp-id      "${EXP_ID}"
}

run_experiment() {
    log "=== experiment phase ==="
    emit_experiment_pairs | \
    parallel "${PARALLEL_OPTS[@]}" --colsep ':::'  \
        python -m kompyle_bench experiment         \
            --cnf         {1}                      \
            --backend     {2}                      \
            --semiring    "${SEMIRINGS[0]}"        \
            --device      "${DEVICES[0]}"          \
            --nb-repeats  "${NB_REPEATS}"          \
            --batch-size  "${BATCH}"               \
            --exp-id      "${EXP_ID}"
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
