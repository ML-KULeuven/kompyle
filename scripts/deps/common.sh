#!/bin/bash

# ---------------------------------------------------------------------------
# system-wide: /usr/local
# user: PREFIX="$HOME/.local"
# HPC:  PREFIX="${VSC_SCRATCH}/install"
# ---------------------------------------------------------------------------
export PREFIX="${PREFIX:-/usr/local}"

export BUILD_TYPE="${BUILD_TYPE:-Release}"

if [ -z "${SUDO+x}" ]; then
  [ "$(id -u)" = "0" ] && export SUDO="" || export SUDO="sudo"
fi

export NPROC
if [[ "$(uname)" == "Linux" ]]; then
  NPROC=$(nproc)
else
  NPROC=$(sysctl -n hw.ncpu)
fi

# ---------------------------------------------------------------------------
# Make PREFIX visible to cmake, pkg-config and the linker for all dep
# scripts that run after this file is sourced.
# ---------------------------------------------------------------------------
export CMAKE_INSTALL_PREFIX="${PREFIX}"
export PKG_CONFIG_PATH="${PREFIX}/lib/pkgconfig:${PKG_CONFIG_PATH:-}"
export LD_LIBRARY_PATH="${PREFIX}/lib:${LD_LIBRARY_PATH:-}"
export PATH="${PREFIX}/bin:${PATH}"

ldconfig_if_linux() {
  [[ "$(uname)" == "Linux" ]] && ldconfig
  return 0
}

cleanup() {
  rm -rf "$@"
}
