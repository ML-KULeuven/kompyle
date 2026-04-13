#!/bin/bash
set -euo pipefail

DEPS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DEPS_DIR/common.sh"

git clone -b ref/clean-up https://github.com/IbrahimElk/d4v2

cd d4v2
cmake --preset release
cmake --build --preset release -j$(nproc)
$SUDO cmake --install build-release

cd ../..
ldconfig_if_linux
