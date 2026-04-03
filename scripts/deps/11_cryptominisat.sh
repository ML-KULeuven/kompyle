#!/bin/bash
set -euo pipefail

DEPS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DEPS_DIR/common.sh"

git clone \
  --revision=4c377ecab94ca9e9d3b2348204fb0ffe27fe6dec \
  --depth=1 https://github.com/msoos/cryptominisat.git

cd cryptominisat && mkdir build && cd build
cmake \
  -DCMAKE_BUILD_TYPE=$BUILD_TYPE \
  -DENABLE_TESTING=OFF \
  -DSTATICCOMPILE=OFF \
  ..
cmake --build . -j$NPROC --config $BUILD_TYPE
$SUDO cmake --install .
cd ../..
ldconfig_if_linux
