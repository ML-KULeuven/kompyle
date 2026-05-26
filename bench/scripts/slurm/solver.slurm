#!/bin/bash -l
# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2
#
# Unified solver-array SLURM script.
#
# Required env vars (set by submit_*.sh via --export=):
#   MODE           synth | real
#   BENCH_STAGE    compile | count
#   EXP_ID         experiment id
#   BENCHMARK_DIR  repo's benchmark/ on scratch
#
# Additional vars for MODE=real:
#   INSTANCES_DIR, PROBLEMS_FILE
#
# Stage-specific knobs:
#   compile:  TIMEOUT (default 1800)
#   count:    TIMEOUT (default 300)
#
# Tuning knobs (optional):
#   OFFSET         added to SLURM_ARRAY_TASK_ID for chunked submissions

#SBATCH --job-name=kc_solve
#SBATCH --output=logs/solve_%A_%a.out
#SBATCH --error=logs/solve_%A_%a.err
#SBATCH --time=0-00:30:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
# --mem is set by the submit script on the sbatch command line

set -euo pipefail
mkdir -p logs

# -----------------------------------------------------------------
# load cluster modules + activate venv
# -----------------------------------------------------------------

STAGE=compile source "$(dirname "${BASH_SOURCE[0]}")/env.sh"

# -----------------------------------------------------------------
# decode this task's parameters
# -----------------------------------------------------------------

: "${MODE:?MODE must be set}"
: "${BENCH_STAGE:?BENCH_STAGE must be set (compile | count)}"
: "${EXP_ID:?EXP_ID must be set}"
: "${BENCHMARK_DIR:?BENCHMARK_DIR must be set}"

cli_args="$("$(dirname "${BASH_SOURCE[0]}")/_decode_task.sh")"

echo "Task ${SLURM_ARRAY_TASK_ID} (offset ${OFFSET:-0})  stage=${BENCH_STAGE}: ${cli_args}"

# -----------------------------------------------------------------
# run
# -----------------------------------------------------------------

cd "${BENCHMARK_DIR}"

case "${BENCH_STAGE}" in
    compile)
        MEM_MB="${SLURM_MEM_PER_NODE}"
        TIMEOUT="${TIMEOUT:-1800}"
        echo "    mem_mb=${MEM_MB}  timeout=${TIMEOUT}"
        python -m kompyle_bench compile \
            ${cli_args} \
            --exp-id  "${EXP_ID}" \
            --mem-mb  "${MEM_MB}" \
            --timeout "${TIMEOUT}"
        ;;
    count)
        MEM_MB="${SLURM_MEM_PER_NODE}"
        TIMEOUT="${TIMEOUT:-300}"
        echo "    mem_mb=${MEM_MB}  timeout=${TIMEOUT}"
        python -m kompyle_bench count \
            ${cli_args} \
            --exp-id  "${EXP_ID}" \
            --mem-mb  "${MEM_MB}" \
            --timeout "${TIMEOUT}"
        ;;
    *)
        echo "ERROR: unknown BENCH_STAGE=${BENCH_STAGE}" >&2
        exit 1
        ;;
esac

echo "$(date '+%Y-%m-%d %H:%M:%S') - Done: task ${SLURM_ARRAY_TASK_ID}"
