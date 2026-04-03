#!/bin/bash
set -euo pipefail

DEPS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DEPS_DIR/common.sh"

wget -q https://github.com/mlpack/ensmallen/archive/refs/tags/2.22.2.tar.gz
tar xf 2.22.2.tar.gz
cd ensmallen-2.22.2 && mkdir build && cd build
cmake -DCMAKE_POLICY_VERSION_MINIMUM=3.5 ..
cmake --build . -j$NPROC --config $BUILD_TYPE
$SUDO cmake --install . --config $BUILD_TYPE
cd ../..
cleanup ensmallen-2.22.2 2.22.2.tar.gz
