#!/bin/bash
set -euo pipefail

DEPS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DEPS_DIR/common.sh"

wget -q https://github.com/flintlib/flint/releases/download/v3.2.0-rc1/flint-3.2.0-rc1.tar.gz
tar xzf flint-3.2.0-rc1.tar.gz
cd flint-3.2.0-rc1
./configure --enable-shared
make -j$NPROC
$SUDO make install
cd ..
cleanup flint-3.2.0-rc1 flint-3.2.0-rc1.tar.gz
ldconfig_if_linux
