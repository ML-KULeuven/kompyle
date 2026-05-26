#!/bin/bash
set -euo pipefail

DEPS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DEPS_DIR/common.sh"
enter_build_dir

log_info "cloning d4v2 (fix/support-mac-platform branch)"
if [ ! -d d4v2/.git ]; then
  run_cmd git clone --depth=1 --branch fix/support-mac-platform \
    https://github.com/IbrahimElk/d4v2
fi
cd d4v2

log_info "configuring"
run_cmd cmake -S . -B build \
  -DCMAKE_BUILD_TYPE=$BUILD_TYPE \
  -DCMAKE_INSTALL_PREFIX="${PREFIX}" \
  -DENABLE_TESTING=OFF

log_info "building ($NPROC cores)"
run_cmd cmake --build build -j$NPROC

log_info "installing"
# run_cmd $SUDO cmake --install build
run_cmd cmake --install build

cd "$BUILD_DIR"
run_cmd ldconfig_if_linux
log_info "d4v2 installed -> $PREFIX"
