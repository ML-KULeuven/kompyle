#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPS_DIR="$SCRIPT_DIR/deps"

bash "$DEPS_DIR/00_system.sh"
bash "$DEPS_DIR/01_gmp.sh"
bash "$DEPS_DIR/02_mpfr.sh"
bash "$DEPS_DIR/03_flint.sh"
bash "$DEPS_DIR/04_cereal.sh"
bash "$DEPS_DIR/05_armadillo.sh"
bash "$DEPS_DIR/06_ensmallen.sh"
bash "$DEPS_DIR/07_mlpack.sh"
bash "$DEPS_DIR/08_cadical.sh"
bash "$DEPS_DIR/09_cadiback.sh"
bash "$DEPS_DIR/10_breakid.sh"
bash "$DEPS_DIR/11_cryptominisat.sh"
bash "$DEPS_DIR/12_sbva.sh"
bash "$DEPS_DIR/13_arjun.sh"
bash "$DEPS_DIR/14_approxmc.sh"
bash "$DEPS_DIR/15_ganak.sh"
bash "$DEPS_DIR/16_sdd.sh"
