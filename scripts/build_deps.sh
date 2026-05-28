#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPS_DIR="$SCRIPT_DIR/deps"
source "$DEPS_DIR/common.sh"

DEPS=(
  00_system.sh
  01_boost.sh
  01_gmp.sh
  02_mpfr.sh
  03_flint.sh
  04_cereal.sh
  05_armadillo.sh
  06_ensmallen.sh
  07_mlpack.sh
  08_cadical.sh
  09_cadiback.sh
  10_breakid.sh
  11_cryptominisat.sh
  12_sbva.sh
  13_arjun.sh
  14_approxmc.sh
  15_ganak.sh
  17_d4v2.sh
)

for d in "${DEPS[@]}"; do
  bash "$DEPS_DIR/$d"
done
