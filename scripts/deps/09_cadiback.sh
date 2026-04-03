#!/bin/bash
set -euo pipefail

DEPS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DEPS_DIR/common.sh"

git clone \
  --revision=a44d5a94c8b8c2c4c8c77116ce80d2bb3a974252 \
  --depth=1 https://github.com/meelgroup/cadiback

cd cadiback
CXX=c++ ./configure
make -j$NPROC
$SUDO cp libcadiback.a /usr/local/lib/
cd ..
ldconfig_if_linux
