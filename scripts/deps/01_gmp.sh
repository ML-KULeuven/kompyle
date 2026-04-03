#!/bin/bash
set -euo pipefail

DEPS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DEPS_DIR/common.sh"

wget -q https://ftp.gnu.org/gnu/gmp/gmp-6.3.0.tar.xz
tar xf gmp-6.3.0.tar.xz
cd gmp-6.3.0
./configure --enable-cxx --enable-shared
make -j$NPROC
$SUDO make install
cd ..
cleanup gmp-6.3.0 gmp-6.3.0.tar.xz
ldconfig_if_linux
