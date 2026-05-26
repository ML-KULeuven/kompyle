#!/usr/bin/env bash
# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2
#
# Cluster-specific SBATCH defaults exported as environment variables.
# SLURM honours SBATCH_* env vars as if they were #SBATCH directives, so
# putting them here means the .slurm scripts only carry the *job-specific*
# directives (time, mem, array, ...).
#
# Source this from your shell or `--export=` it from submit scripts.

export SBATCH_CLUSTERS="wice"
export SBATCH_ACCOUNT="lp_dtai1"
export SBATCH_PARTITION="batch"
export SBATCH_MAIL_USER="ibrahim.elkaddouri@student.kuleuven.be"
export SBATCH_MAIL_TYPE="NONE"
