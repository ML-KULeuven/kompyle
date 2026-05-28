#!/usr/bin/env bash
# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2
#
# Cluster-specific SBATCH defaults exported as environment variables.
# Source this from your shell or `--export=` it from submit scripts.

export SBATCH_CLUSTERS="wice"
export SBATCH_ACCOUNT="X"
export SBATCH_PARTITION="batch"
export SBATCH_MAIL_USER="X.Y@Z"
export SBATCH_MAIL_TYPE="NONE"
