#!/bin/bash
set -euo pipefail

DEPS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DEPS_DIR/common.sh"

git clone --depth=1 --branch 4.7.0 https://github.com/mlpack/mlpack.git
cd mlpack && mkdir build && cd build
cmake \
  -DCMAKE_BUILD_TYPE=$BUILD_TYPE \
  -DBUILD_SHARED_LIBS=ON \
  -DBUILD_CLI_EXECUTABLES=OFF \
  ..
cmake --build . -j$NPROC --config $BUILD_TYPE
$SUDO cmake --install . --config $BUILD_TYPE
cd ../..
cleanup mlpack
ldconfig_if_linux
