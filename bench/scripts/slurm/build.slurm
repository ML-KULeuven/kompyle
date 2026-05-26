#!/bin/bash -l
# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2
#
# Create a venv and pip-install kompyle from TestPyPI.
# Run once per cluster (or per kompyle version bump).
#
# Site-specific defaults (cluster, account, mail) come from
# scripts/slurm/sbatch_defaults.sh, source that before sbatch'ing.

#SBATCH --job-name=kc_build
#SBATCH --output=logs/build_%j.out
#SBATCH --error=logs/build_%j.err
#SBATCH --time=0-00:15:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G

set -euo pipefail
mkdir -p logs

# Load Python + define $VENV.
STAGE=build source "${SLURM_SUBMIT_DIR}/scripts/slurm/env.sh"

# Pin the kompyle version here. Bump and re-sbatch when upgrading.
KOMPYLE_VERSION="${KOMPYLE_VERSION:-0.0.1.dev115}"

# Re-create the venv from scratch so version bumps can't leave stale deps.
rm -rf "${VENV}"
python3 -m venv "${VENV}"
# shellcheck disable=SC1091
source "${VENV}/bin/activate"

pip install --upgrade pip

# kompyle lives on TestPyPI; its dependencies (numpy, klay, ...) live on
# the real PyPI, so we point at both.
pip install "kompyle==${KOMPYLE_VERSION}" \
    --index-url       https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple

# Benchmark-only extras.
pip install pysdd numpy pandas matplotlib tqdm torch

echo "=== build complete (kompyle ${KOMPYLE_VERSION}) ==="
