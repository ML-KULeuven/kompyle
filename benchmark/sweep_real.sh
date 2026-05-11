#!/usr/bin/env bash
# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2

set -euo pipefail

EXP_ID="${1:?Usage: bash sweep_real.sh <exp_id> [phase]}"
PHASE="${2:-all}"
shift 2 || true

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BENCHMARK_DIR="${BENCHMARK_DIR:-${SCRIPT_DIR}}"
INSTANCES_DIR="${INSTANCES_DIR:-${BENCHMARK_DIR}/assets}"
PROBLEMS_FILE="${BENCHMARK_DIR}/assets/all_problems.txt"

if [[ ! -f "${PROBLEMS_FILE}" ]]; then
    echo "ERROR: problems file not found: ${PROBLEMS_FILE}" >&2
    exit 1
fi

BACKENDS=(ganak ganak_arjun d4v2 sdd)
SEMIRINGS=(real log)
DEVICE=(cpu cuda)
BATCH=32
NB_REPEATS=10
COLLAPSE=0
MERGE=0
VERIFY=0

MEM_MB="${MEM_MB:-5000}"
TIMEOUT="${TIMEOUT:-10}"

PARALLEL_OPTS=(
    --eta
    --line-buffer
    --jobs 4
    # --halt now,fail=1
    # --memfree 10G
    # --noswap
    "$@"
)

mapfile -t PROBLEMS < "${PROBLEMS_FILE}"
N_PROBLEMS=${#PROBLEMS[@]}
echo "Problems: ${N_PROBLEMS}  Backends: ${#BACKENDS[@]}"
echo "Total compile tasks: $(( N_PROBLEMS * ${#BACKENDS[@]} ))"

run_compile() {
    echo "=== compile phase ==="

    local pairs=()
    for problem in "${PROBLEMS[@]}"; do
        local cnf_path="${INSTANCES_DIR}/${problem}"
        if [[ ! -f "${cnf_path}" ]]; then
            echo "WARN: missing instance, skipping: ${cnf_path}" >&2
            continue
        fi
        for backend in "${BACKENDS[@]}"; do
            pairs+=("${cnf_path}:::${backend}")
        done
    done

    printf '%s\n' "${pairs[@]}" | \
    parallel "${PARALLEL_OPTS[@]}"                          \
        --colsep ':::'                                      \
        python "${BENCHMARK_DIR}/mainc.py"                  \
            --cnf     {1}                                   \
            --backend {2}                                   \
            --exp-id  "${EXP_ID}"                           \
            --timeout "${TIMEOUT}"                          \
            --mem-mb  "${MEM_MB}"
}

run_infer() {
    echo "=== infer phase ==="

    local pairs=()
    for problem in "${PROBLEMS[@]}"; do
        local cnf_path="${INSTANCES_DIR}/${problem}"
        [[ -f "${cnf_path}" ]] || continue
        for backend in "${BACKENDS[@]}"; do
            for semiring in "${SEMIRINGS[@]}"; do
                for device in "${DEVICE[@]}"; do
                    pairs+=("${cnf_path}:::${backend}:::${semiring}:::${device}")
                done
            done
        done
    done

    printf '%s\n' "${pairs[@]}" | \
    parallel "${PARALLEL_OPTS[@]}"                          \
        --colsep ':::'                                      \
        python "${BENCHMARK_DIR}/maini.py"                  \
            --cnf        {1}                                \
            --backend    {2}                                \
            --semiring   {3}                                \
            --device     {4}                                \
            --batch-size "${BATCH}"                         \
            --exp-id     "${EXP_ID}"                        \
            --collapse   "${COLLAPSE}"                      \
            --merge      "${MERGE}"                         \
            --verify     "${VERIFY}"
}

run_experiment() {
    echo "=== experiment phase ==="

    local pairs=()
    for problem in "${PROBLEMS[@]}"; do
        local cnf_path="${INSTANCES_DIR}/${problem}"
        [[ -f "${cnf_path}" ]] || continue
        for backend in "${BACKENDS[@]}"; do
            pairs+=("${cnf_path}:::${backend}")
        done
    done

    printf '%s\n' "${pairs[@]}" | \
    parallel "${PARALLEL_OPTS[@]}"                          \
        --colsep ':::'                                      \
        python "${BENCHMARK_DIR}/maine.py"                  \
            --cnf        {1}                                \
            --backend    {2}                                \
            --semiring   "${SEMIRINGS[0]}"                  \
            --device     "${DEVICE[0]}"                     \
            --nb-repeats "${NB_REPEATS}"                    \
            --batch-size "${BATCH}"                         \
            --exp-id     "${EXP_ID}"                        \
            --collapse   "${COLLAPSE}"                      \
            --merge      "${MERGE}"
}

case "${PHASE}" in
    compile)    run_compile    ;;
    infer)      run_infer      ;;
    experiment) run_experiment ;;
    all)
        run_compile
        run_infer
        run_experiment
        ;;
    *)
        echo "Unknown phase: ${PHASE}" >&2
        echo "Valid phases: compile | infer | experiment | all" >&2
        exit 1
        ;;
esac

echo "=== done ==="
