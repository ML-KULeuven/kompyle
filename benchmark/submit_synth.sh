#!/usr/bin/env bash
set -euo pipefail

EXP_ID="${1:?Usage: bash submit_synth.sh <exp_id> [mem_gb]}"
MEM_GB="${2:-32}"

BENCHMARK="${VSC_DATA}/kompyle/benchmark"
HPC_SCRIPTS="${VSC_DATA}/scripts/hpc"

echo "Syncing repository to scratch..."
rsync -av --exclude='__pycache__' --exclude='*.pyc' --exclude='.git' \
    "${VSC_DATA}/kompyle/" \
    "${VSC_SCRATCH}/kompyle/"

BENCHMARK_SCRATCH="${VSC_SCRATCH}/kompyle/benchmark"

# 11 x 6 x 4 x 4 = 1056 tasks
echo "Submitting synth array: exp_id=${EXP_ID}  tasks=0-1055  mem=${MEM_GB}G"

job_id=$(sbatch \
    --array=0-1055 \
    --mem="${MEM_GB}G" \
    --export=ALL,EXP_ID="${EXP_ID}",BENCHMARK_DIR="${BENCHMARK_SCRATCH}" \
    --parsable \
    "${HPC_SCRIPTS}/compile_synth.slurm" | cut -d';' -f1)

echo "Submitted job ${job_id}"
echo "Monitor: squeue -j ${job_id}"
echo "Logs:    logs/compile_synth_${job_id}_*.{out,err}"
