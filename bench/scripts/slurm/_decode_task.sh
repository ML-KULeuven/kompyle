#!/usr/bin/env bash
# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2
#
# Decode a flat SLURM_ARRAY_TASK_ID into the corresponding sweep
# parameters and emit them as a CLI fragment for the unified runner.
#
# Reads:
#   MODE                 synth | real
#   BENCH_STAGE          compile | count  (selects which backend array to iterate)
#   SLURM_ARRAY_TASK_ID  index into the (offset + task_id)-th task
#   OFFSET               added to SLURM_ARRAY_TASK_ID (chunked submissions)
#
# Synth mode also reads NB_VARS/RATIOS/SEEDS and {BACKENDS,COUNT_BACKENDS}
# from grid.sh.
#
# Real mode also reads:
#   PROBLEMS_FILE        list of CNF paths relative to INSTANCES_DIR
#   INSTANCES_DIR
#
# Writes one line of `--flag value` pairs to stdout:
#   synth: --nb-vars N --ratio R --seed S --backend B
#   real:  --cnf PATH --backend B

set -euo pipefail

: "${MODE:?MODE must be set (synth | real)}"
: "${SLURM_ARRAY_TASK_ID:?must be set}"

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${script_dir}/../lib/grid.sh"

bench_stage="${BENCH_STAGE:-compile}"
case "${bench_stage}" in
    compile) backend_list=("${BACKENDS[@]}") ;;
    count)   backend_list=("${COUNT_BACKENDS[@]}") ;;
    *)
        echo "ERROR: unknown BENCH_STAGE=${bench_stage}  (valid: compile | count)" >&2
        exit 1
        ;;
esac

tid=$(( SLURM_ARRAY_TASK_ID + ${OFFSET:-0} ))

case "${MODE}" in
    synth)
        n_backends=${#backend_list[@]}
        n_seeds=${#SEEDS[@]}
        n_ratios=${#RATIOS[@]}

        i_backend=$(( tid % n_backends )); tid=$(( tid / n_backends ))
        i_seed=$((    tid % n_seeds    )); tid=$(( tid / n_seeds    ))
        i_ratio=$((   tid % n_ratios   )); tid=$(( tid / n_ratios   ))
        i_vars=${tid}

        printf -- '--nb-vars %s --ratio %s --seed %s --backend %s\n' \
            "${NB_VARS[$i_vars]}" \
            "${RATIOS[$i_ratio]}" \
            "${SEEDS[$i_seed]}" \
            "${backend_list[$i_backend]}"
        ;;

    real)
        : "${PROBLEMS_FILE:?must be set in real mode}"
        : "${INSTANCES_DIR:?must be set in real mode}"
        mapfile -t PROBLEMS < "${PROBLEMS_FILE}"
        n_backends=${#backend_list[@]}

        i_backend=$(( tid % n_backends ))
        i_problem=$(( tid / n_backends ))

        printf -- '--cnf %s --backend %s\n' \
            "${INSTANCES_DIR}/${PROBLEMS[$i_problem]}" \
            "${backend_list[$i_backend]}"
        ;;

    *)
        echo "ERROR: unknown MODE=${MODE}  (valid: synth | real)" >&2
        exit 1
        ;;
esac
