#!/bin/bash
set -euo pipefail

DEPS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DEPS_DIR/common.sh"

git clone \
  --revision=729939aba815b1837b1590279e66c61ed9d3092f \
  --depth=1 https://github.com/meelgroup/cadical.git

cd cadical
CXXFLAGS="-fPIC" ./configure --competition
make -j$NPROC
mkdir -p "${PREFIX}/lib"    "${PREFIX}/include/cadical"
$SUDO cp build/libcadical.a "${PREFIX}/lib/"
$SUDO cp src/cadical.hpp    "${PREFIX}/include/cadical/"
cd ..
ldconfig_if_linux
