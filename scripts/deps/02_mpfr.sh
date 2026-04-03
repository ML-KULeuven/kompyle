#!/bin/bash
set -euo pipefail

DEPS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DEPS_DIR/common.sh"

wget -q https://ftp.gnu.org/gnu/mpfr/mpfr-4.2.1.tar.xz
tar xJf mpfr-4.2.1.tar.xz
cd mpfr-4.2.1
./configure --enable-cxx --enable-shared
make -j$NPROC
$SUDO make install
cd ..
cleanup mpfr-4.2.1 mpfr-4.2.1.tar.xz
ldconfig_if_linux
