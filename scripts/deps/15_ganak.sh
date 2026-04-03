#!/bin/bash
set -euo pipefail

DEPS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DEPS_DIR/common.sh"

git clone \
  --revision=4b6037d2efbbcbb8ae30f4b2d670bfaeff4a284d \
  --depth=1 https://github.com/IbrahimElk/ganak

cd ganak && mkdir build && cd build
cmake \
  -DCMAKE_BUILD_TYPE=$BUILD_TYPE \
  -DENABLE_TESTING=OFF \
  -DSTATICCOMPILE=OFF \
  ..
cmake --build . -j$NPROC --config $BUILD_TYPE
$SUDO cmake --install . --config $BUILD_TYPE
cd ../..
ldconfig_if_linux
