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
$SUDO cp build/libcadical.a /usr/local/lib/
cd ..
ldconfig_if_linux
