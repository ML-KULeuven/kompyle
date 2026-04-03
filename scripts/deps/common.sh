#!/bin/bash

export BUILD_TYPE="Release"

export NPROC
if [[ "$(uname)" == "Linux" ]]; then
  NPROC=$(nproc)
else
  NPROC=$(sysctl -n hw.ncpu)
fi

export SUDO=""
if [ "$(id -u)" != "0" ]; then
  SUDO="sudo"
fi

ldconfig_if_linux() {
  [[ "$(uname)" == "Linux" ]] && ldconfig
  return 0
}

cleanup() {
  rm -rf "$@"
}
