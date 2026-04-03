#!/bin/bash
set -euo pipefail

DEPS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DEPS_DIR/common.sh"

wget -q https://sourceforge.net/projects/arma/files/armadillo-14.0.2.tar.xz
tar xf armadillo-14.0.2.tar.xz
cd armadillo-14.0.2
./configure
make -j$NPROC
$SUDO make install
cd ..
cleanup armadillo-14.0.2 armadillo-14.0.2.tar.xz
ldconfig_if_linux
