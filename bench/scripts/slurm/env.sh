#!/usr/bin/env bash
# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2
#
# HPC cluster environment setup, sourced from every .slurm script.

set -euo pipefail

: "${VSC_SCRATCH:?VSC_SCRATCH must be set}"
: "${VSC_DATA:?VSC_DATA must be set}"

export VENV="${VSC_SCRATCH}/venv"
export REPO_DATA="${VSC_DATA}/kompyle"
export REPO_SCRATCH="${VSC_SCRATCH}/kompyle"

module load Python/3.12.3-GCCcore-13.3.0

stage="${STAGE:-compile}"
case "${stage}" in
    build)
        # build.slurm creates the venv itself.
        ;;
    compile)
        [[ -d "${VENV}" ]] || {
          echo "ERROR: venv not found at ${VENV} (run build.slurm first)" >&2; exit 1;
        }
        source "${VENV}/bin/activate"
        ;;
    *)
        echo "ERROR: unknown STAGE='${stage}' (valid: build | compile)" >&2
        exit 1
        ;;
esac
