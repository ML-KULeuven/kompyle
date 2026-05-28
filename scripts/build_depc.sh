#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPS_DIR="$SCRIPT_DIR/deps"

usage() {
  cat <<EOF
Usage: build_depc [OPTIONS]

Options:
  --prefix PATH        Installation prefix (required)
  --build-type TYPE    CMake build type: Release|Debug|RelWithDebInfo (default: Release)
  --build-dir PATH     Scratch dir for downloads & builds
                       (default: /tmp/kompyle-deps for /usr|/opt prefix,
                                 ~/.cache/kompyle-deps for \$HOME prefix,
                                 <dirname of prefix>/kompyle-deps otherwise)
  --sudo CMD           Sudo command to use, or empty string to disable (default: auto)
  --verbose, -v        Stream full tool output (default: silent; failures still dump tail)
  -h, --help           Show this help message
EOF
  exit 0
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --prefix)       export PREFIX="$2";     shift 2 ;;
    --build-type)   export BUILD_TYPE="$2"; shift 2 ;;
    --build-dir)    export BUILD_DIR="$2";  shift 2 ;;
    --sudo)         export SUDO="$2";       shift 2 ;;
    --verbose|-v)   export VERBOSE=1;       shift ;;
    -h|--help)      usage ;;
    *) echo "Unknown option: $1" >&2; usage ;;
  esac
done

if [[ -z "${PREFIX:-}" ]]; then
  echo "Error: --prefix is required" >&2
  usage
fi

export BUILD_TYPE="${BUILD_TYPE:-Release}"
source "$DEPS_DIR/common.sh"

log_info "PREFIX      = $PREFIX"
log_info "BUILD_TYPE  = $BUILD_TYPE"
log_info "BUILD_DIR   = $BUILD_DIR"
log_info "SUDO        = ${SUDO:-(auto)}"
log_info "VERBOSE     = ${VERBOSE:-0}"

DEPS=(
  "00_system.sh:system packages"
  "01_boost.sh:boost 1.90.0"
  "01_gmp.sh:gmp 6.3.0"
  "02_mpfr.sh:mpfr 4.2.1"
  "03_flint.sh:flint 3.2.0-rc1"
  "04_cereal.sh:cereal 1.3.2"
  "05_armadillo.sh:armadillo 14.0.2"
  "06_ensmallen.sh:ensmallen 2.22.2"
  "07_mlpack.sh:mlpack 4.7.0"
  "08_cadical.sh:cadical"
  "09_cadiback.sh:cadiback"
  "10_breakid.sh:breakid"
  "11_cryptominisat.sh:cryptominisat"
  "12_sbva.sh:sbva"
  "13_arjun.sh:arjun"
  "14_approxmc.sh:approxmc"
  "15_ganak.sh:ganak"
  "17_d4v2.sh:d4v2"
)

N=${#DEPS[@]}
for i in "${!DEPS[@]}"; do
  IFS=':' read -r script label <<< "${DEPS[$i]}"
  log_step "$(printf '%02d/%02d' "$((i+1))" "$N") $label"
  bash "$DEPS_DIR/$script"
done

log_info "all done. scratch tree: $BUILD_DIR (safe to remove)"
