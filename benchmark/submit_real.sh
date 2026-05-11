#!/usr/bin/env bash
set -euo pipefail

EXP_ID="${1:?Usage: bash submit_real.sh <exp_id> [mem_gb]}"
MEM_GB="${2:-32}"

HPC_SCRIPTS="${VSC_DATA}/scripts/hpc"

echo "Syncing repository to scratch..."
rsync -av --exclude='__pycache__' --exclude='*.pyc' --exclude='.git' \
    "${VSC_DATA}/kompyle/" \
    "${VSC_SCRATCH}/kompyle/"

BENCHMARK_SCRATCH="${VSC_SCRATCH}/kompyle/benchmark"
INSTANCES_DIR="${VSC_SCRATCH}/instances"

N_PROBLEMS=$(wc -l < "${BENCHMARK_SCRATCH}/assets/all_problems.txt")
LAST=$(( N_PROBLEMS * 4 - 1 ))

echo "Submitting real array: exp_id=${EXP_ID}  tasks=0-${LAST}  mem=${MEM_GB}G"

job_id=$(sbatch \
    --array=0-"${LAST}" \
    --mem="${MEM_GB}G" \
    --export=ALL,EXP_ID="${EXP_ID}",INSTANCES_DIR="${INSTANCES_DIR}",BENCHMARK_DIR="${BENCHMARK_SCRATCH}" \
    --parsable \
    "${HPC_SCRIPTS}/compile_real.slurm" | cut -d';' -f1)

echo "Submitted job ${job_id}"
echo "Monitor: squeue -j ${job_id}"
echo "Logs:    logs/compile_real_${job_id}_*.{out,err}"
