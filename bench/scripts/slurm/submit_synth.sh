#!/usr/bin/env bash
# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2
#
# Submit a synthetic-sweep solver array on the HPC.
# Run from the login node after build.slurm has finished.
#
# Usage:
#   bash scripts/slurm/submit_synth.sh <exp_id> [stage] [mem_gb]
#
# stage:   compile (default) | count
# mem_gb:  default 32  (count typically needs less; pass e.g. 8)
#
# Examples:
#   bash scripts/slurm/submit_synth.sh 7
#   bash scripts/slurm/submit_synth.sh 7 count 8

set -euo pipefail

EXP_ID="${1:?Usage: $0 <exp_id> [stage] [mem_gb]}"
BENCH_STAGE="${2:-compile}"
MEM_GB="${3:-32}"

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

BENCHMARK_SCRATCH="${VSC_SCRATCH}/kompyle/benchmark"

# ----------------------------------------------------------------------------
# compute total tasks to do
# ----------------------------------------------------------------------------

if [[ "${BENCH_STAGE}" == "compile" ]]; then
    TOTAL=$(synth_n_compile_tasks)
else
    TOTAL=$(synth_n_count_tasks)
fi
log "Submitting synth ${BENCH_STAGE} array: exp_id=${EXP_ID}  tasks=${TOTAL}  mem=${MEM_GB}G"

# ----------------------------------------------------------------------------
# submit
# ----------------------------------------------------------------------------

chunked_submit                                                              \
    --slurm-file "${script_dir}/solver.slurm"                               \
    --total      "${TOTAL}"                                                 \
    --mem        "${MEM_GB}G"                                               \
    --chunk      212                                                        \
    --export     "ALL,MODE=synth,BENCH_STAGE=${BENCH_STAGE},EXP_ID=${EXP_ID},BENCHMARK_DIR=${BENCHMARK_SCRATCH}"

cat <<EOF

Monitor: squeue --clusters=wice -u \$USER
Logs:    ${BENCHMARK_SCRATCH}/logs/solve_<jobid>_<taskid>.{out,err}
EOF
