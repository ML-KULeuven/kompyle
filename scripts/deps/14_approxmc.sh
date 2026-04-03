#!/bin/bash
set -euo pipefail

DEPS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DEPS_DIR/common.sh"

git clone \
  --revision=e1cd45156639c6ca794b14050d5ca546921e7455 \
  --depth=1 https://github.com/meelgroup/approxmc

cd approxmc && mkdir build && cd build
cmake \
  -DCMAKE_BUILD_TYPE=$BUILD_TYPE \
  -DENABLE_TESTING=OFF \
  -DSTATICCOMPILE=OFF \
  ..
cmake --build . -j$NPROC --config $BUILD_TYPE
$SUDO cmake --install . --config $BUILD_TYPE
cd ../..
ldconfig_if_linux
