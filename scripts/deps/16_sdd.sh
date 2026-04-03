#!/bin/bash
set -euo pipefail

DEPS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DEPS_DIR/common.sh"

git clone --depth=1 https://github.com/IbrahimElk/sdd

cd sdd && mkdir build && cd build
cmake \
  -DCMAKE_BUILD_TYPE=$BUILD_TYPE \
  ..
cmake --build . -j$NPROC
$SUDO cmake --install .
cd ../..
ldconfig_if_linux
