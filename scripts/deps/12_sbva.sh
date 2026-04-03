#!/bin/bash
set -euo pipefail

DEPS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DEPS_DIR/common.sh"

git clone \
  --revision=52c1835773cb97edab25dfaa7c27d23ba1e5b71e \
  --depth=1 https://github.com/meelgroup/SBVA

cd SBVA && mkdir build && cd build
cmake \
  -DCMAKE_BUILD_TYPE=$BUILD_TYPE \
  -DENABLE_TESTING=OFF \
  -DSTATICCOMPILE=OFF \
  ..
cmake --build . -j$NPROC --config $BUILD_TYPE
$SUDO cmake --install .
cd ../..
ldconfig_if_linux
