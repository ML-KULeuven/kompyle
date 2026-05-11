#!/bin/bash -l

#SBATCH --clusters=wice
#SBATCH --account=lp_dtai1
#SBATCH --job-name=kc_compile_real

#SBATCH --mail-user=ibrahim.elkaddouri@student.kuleuven.be
#SBATCH --mail-type=NONE

#SBATCH --output=logs/compile_real_%A_%a.out
#SBATCH --error=logs/compile_real_%A_%a.err

#SBATCH --time=0-00:30:00

#SBATCH --partition=batch
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
# --mem is set by submit_real.sh on the sbatch command line

set -euo pipefail
mkdir -p logs

BACKENDS=(ganak ganak_arjun d4v2 sdd)
N_BACKENDS=${#BACKENDS[@]}

PROBLEMS_FILE="${BENCHMARK_DIR}/assets/all_problems.txt"
mapfile -t PROBLEMS < "${PROBLEMS_FILE}"

tid=${SLURM_ARRAY_TASK_ID}
i_backend=$(( tid % N_BACKENDS ))
i_problem=$(( tid / N_BACKENDS ))

BACKEND=${BACKENDS[$i_backend]}
CNF_PATH="${INSTANCES_DIR}/${PROBLEMS[$i_problem]}"

MEM_MB=${SLURM_MEM_PER_NODE}

echo "Task ${SLURM_ARRAY_TASK_ID}: backend=${BACKEND}  cnf=${CNF_PATH}  mem_mb=${MEM_MB}"

# ---------------------------------------------------------------------------
module load Python
module load SciPy-bundle
source "${VSC_SCRATCH}/venv/bin/activate"
export LD_LIBRARY_PATH="${VSC_SCRATCH}/install/lib:${LD_LIBRARY_PATH:-}"

# ---------------------------------------------------------------------------
cd "${VSC_SCRATCH}/kompyle/benchmark"

python "${BENCHMARK_DIR}/mainc.py" \
    --cnf     "${CNF_PATH}"        \
    --backend "${BACKEND}"         \
    --exp-id  "${EXP_ID}"          \
    --mem-mb  "${MEM_MB}"

echo "$(date '+%Y-%m-%d %H:%M:%S') - Done: task ${SLURM_ARRAY_TASK_ID}"


