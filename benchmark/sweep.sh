#!/usr/bin/env bash
# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2
set -euo pipefail

# 5 * 3 * 4 = 15 * 4 = 60
NB_VARS=(
  30
  35
  40
  45
  50
  55
  60
  65
  70
  75
  80
)
RATIOS=(
  2.5
  3.0
  3.5
  4.0
  4.5
  5.0
)
SEEDS=(0 1 2 3)
BACKENDS=(ganak ganak_arjun d4v2 sdd)
SEMIRINGS=(
  real
  log
)
DEVICE=(cpu cuda)

# BATCH=8
BATCH=32 # not eough VRAM for batch of 32 like klay...
NB_REPEATS=10
COLLAPSE=0
MERGE=0
VERIFY=0

EXP_ID="${1:-}"
PHASE="${2:-all}"
shift || true
shift || true

if [ -z "$EXP_ID" ]; then
    echo "Usage: $0 <exp_id> [phase]"
    exit 1
fi

PARALLEL_OPTS=(
    # --halt now,fail=1
    --eta
    --line-buffer
    --jobs 4
    # --memfree 10G
    # --noswap
    "$@" 
)

run_compile() {
    echo "=== compile phase ==="
    parallel "${PARALLEL_OPTS[@]}"  \
        python mainc.py             \
          --nb-vars {1}             \
          --ratio   {2}             \
          --seed    {3}             \
          --backend {4}             \
          --exp-id "$EXP_ID"        \
    ::: "${NB_VARS[@]}"             \
    ::: "${RATIOS[@]}"              \
    ::: "${SEEDS[@]}"               \
    ::: "${BACKENDS[@]}"
}

run_infer() {
    echo "=== infer phase ==="
    parallel "${PARALLEL_OPTS[@]}"  \
        python maini.py             \
          --nb-vars   {1}           \
          --ratio     {2}           \
          --seed      {3}           \
          --backend   {4}           \
          --semiring  {5}           \
          --device    {6}           \
          --batch-size "${BATCH}"   \
          --exp-id "$EXP_ID"        \
          --collapse "$COLLAPSE"    \
          --merge "$MERGE"          \
          --verify "$VERIFY"     \
    ::: "${NB_VARS[@]}"             \
    ::: "${RATIOS[@]}"              \
    ::: "${SEEDS[@]}"               \
    ::: "${BACKENDS[@]}"            \
    ::: "${SEMIRINGS[@]}"           \
    ::: "${DEVICE[@]}"
}

run_experiment() {
    echo "=== experiment phase ==="
    parallel "${PARALLEL_OPTS[@]}"      \
        python maine.py                 \
          --nb-vars {1}                 \
          --ratio {2}                   \
          --seed {3}                    \
          --backend {4}                 \
          --semiring {5}                \
          --device {6}                  \
          --nb-repeats "${NB_REPEATS}"  \
          --batch-size "${BATCH}"       \
          --exp-id "$EXP_ID"            \
          --collapse "$COLLAPSE"        \
          --merge "$MERGE"              \
    ::: "${NB_VARS[@]}"                 \
    ::: "${RATIOS[@]}"                  \
    ::: "${SEEDS[@]}"                   \
    ::: "${BACKENDS[@]}"                \
    ::: "${SEMIRINGS[0]}"               \
    ::: "${DEVICE[0]}"
}

case "$PHASE" in
    compile)    run_compile    ;;
    infer)      run_infer      ;;
    experiment) run_experiment ;;
    all)
        run_compile
        run_infer
        run_experiment
        ;;
    *)
        echo "Unknown phase: $PHASE"
        exit 1
        ;;
esac

echo "=== done ==="
