#!/usr/bin/env bash
# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2
#
# Helper that submits a large array job in chunks small enough to fit
# under the cluster's per-submission array limit (wice QOS allows 264).
# Each subsequent chunk depends on the previous one finishing.
#
# Usage (from another script):
#   source "scripts/slurm/_chunked_submit.sh"
#   chunked_submit  --slurm-file <path> \
#                   --total <N> \
#                   --mem "32G" \
#                   --chunk 212 \
#                   --export "ALL,EXP_ID=...,..."

set -euo pipefail

chunked_submit() {
    local slurm_file= total= mem= chunk=212 export_=
    while (( $# )); do
        case "$1" in
            --slurm-file) slurm_file="$2"; shift 2 ;;
            --total)      total="$2";      shift 2 ;;
            --mem)        mem="$2";        shift 2 ;;
            --chunk)      chunk="$2";      shift 2 ;;
            --export)     export_="$2";    shift 2 ;;
            *) echo "ERROR: unknown arg: $1" >&2; return 1 ;;
        esac
    done

    [[ -n "${slurm_file}" && -n "${total}" && -n "${mem}" && -n "${export_}" ]] \
        || { echo "ERROR: missing required arg" >&2; return 1; }

    local prev_job=""
    local offset=0
    local n_chunks=0

    while (( offset < total )); do
        n_chunks=$(( n_chunks + 1 ))
        local remaining=$(( total - offset ))
        local n=$(( remaining < chunk ? remaining : chunk ))
        local last=$(( n - 1 ))

        local dep=()
        if [[ -n "${prev_job}" ]]; then
            dep=(--dependency="afterany:${prev_job}")
        fi

        # shellcheck disable=SC2086  # array expansion handles dep correctly
        prev_job=$(sbatch                                       \
            --array=0-${last}                                   \
            --mem="${mem}"                                      \
            "${dep[@]}"                                         \
            --export="${export_},OFFSET=${offset}"              \
            --parsable                                          \
            "${slurm_file}" | cut -d';' -f1)

        echo "  chunk ${n_chunks}: offset=${offset}  size=${n}  job=${prev_job}"
        offset=$(( offset + n ))
    done

    echo "Submitted ${n_chunks} chunks, ${total} total tasks."
}
