#!/bin/bash
set -euo pipefail

DEPS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DEPS_DIR/common.sh"

git clone --depth=1 --branch fix/support-mac-platform \
  https://github.com/IbrahimElk/d4v2

cd d4v2

cmake -S . -B build \
  -DCMAKE_BUILD_TYPE=$BUILD_TYPE \
  -DENABLE_TESTING=OFF
cmake --build build -j$NPROC
$SUDO cmake --install build

# cmake --preset release
# cmake --build --preset release -j$NPROC
# $SUDO cmake --install build-release

cd ../..
ldconfig_if_linux
