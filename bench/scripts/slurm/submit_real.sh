#!/usr/bin/env bash
# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2
#
# Submit a real-instance solver array on the HPC.
# Run from the login node after build.slurm has finished.
#
# Usage:
#   bash scripts/slurm/submit_real.sh <exp_id> [stage] [mem_gb]
#
# stage:   compile (default) | count
# mem_gb:  default 4G

set -euo pipefail

EXP_ID="${1:?Usage: $0 <exp_id> [stage] [mem_gb]}"
BENCH_STAGE="${2:-compile}"
MEM_GB="${3:-4}"

case "${BENCH_STAGE}" in
    compile|count) ;;
    *) echo "ERROR: stage must be compile or count, got: ${BENCH_STAGE}" >&2; exit 1 ;;
esac

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${script_dir}/../lib/common.sh"
source "${script_dir}/../lib/grid.sh"
source "${script_dir}/sbatch_defaults.sh"
source "${script_dir}/_chunked_submit.sh"

# ----------------------------------------------------------------------------
# sync repo to scratch
# ----------------------------------------------------------------------------

: "${VSC_DATA:?VSC_DATA must be set}"
: "${VSC_SCRATCH:?VSC_SCRATCH must be set}"

log "Syncing repository to scratch..."
rsync -a --exclude='__pycache__' --exclude='*.pyc' --exclude='.git' \
    "${VSC_DATA}/kompyle/" "${VSC_SCRATCH}/kompyle/"

BENCHMARK_SCRATCH="${VSC_SCRATCH}/kompyle/bench"
INSTANCES_DIR="${BENCHMARK_SCRATCH}/assets"
PROBLEMS_FILE="${BENCHMARK_SCRATCH}/assets/all_problems.txt"
require_file "${PROBLEMS_FILE}"

# ----------------------------------------------------------------------------
# compute total tasks to do
# ----------------------------------------------------------------------------

N_PROBLEMS=$(wc -l < "${PROBLEMS_FILE}")
if [[ "${BENCH_STAGE}" == "compile" ]]; then
    n_backends=${#BACKENDS[@]}
else
    n_backends=${#COUNT_BACKENDS[@]}
fi
TOTAL=$(( N_PROBLEMS * n_backends ))
log "Problems: ${N_PROBLEMS}  Backends: ${n_backends}"
log "Submitting real ${BENCH_STAGE} array: exp_id=${EXP_ID}  tasks=${TOTAL}  mem=${MEM_GB}G"

# ----------------------------------------------------------------------------
# submit
# ----------------------------------------------------------------------------
chunked_submit                                  \
    --slurm-file "${script_dir}/solver.slurm"   \
    --total      "${TOTAL}"                     \
    --mem        "${MEM_GB}G"                   \
    --chunk      212                            \
    --export     "ALL,MODE=real,BENCH_STAGE=${BENCH_STAGE},EXP_ID=${EXP_ID},BENCHMARK_DIR=${BENCHMARK_SCRATCH},INSTANCES_DIR=${INSTANCES_DIR},PROBLEMS_FILE=${PROBLEMS_FILE}"

cat <<EOF

Monitor: squeue --clusters=wice -u \$USER
Logs:    ${BENCHMARK_SCRATCH}/logs/solve_<jobid>_<taskid>.{out,err}
EOF
