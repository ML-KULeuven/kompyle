#!/bin/bash
set -euo pipefail

DEPS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DEPS_DIR/common.sh"
enter_build_dir

log_info "cloning cryptominisat"
if [ ! -d cryptominisat/.git ]; then
  run_cmd git clone https://github.com/msoos/cryptominisat.git
fi
cd cryptominisat

log_info "checking out pinned commit"
run_cmd git checkout 4c377ecab94ca9e9d3b2348204fb0ffe27fe6dec

mkdir -p build && cd build

log_info "configuring"
run_cmd cmake \
  -DCMAKE_INSTALL_PREFIX="${PREFIX}" \
  -DCMAKE_BUILD_TYPE=$BUILD_TYPE \
  -DENABLE_TESTING=OFF \
  -DSTATICCOMPILE=OFF \
  ..

log_info "building ($NPROC cores)"
run_cmd cmake --build . -j$NPROC --config $BUILD_TYPE

log_info "installing"
# run_cmd $SUDO cmake --install . --config $BUILD_TYPE
run_cmd cmake --install . --config $BUILD_TYPE

cd "$BUILD_DIR"
run_cmd ldconfig_if_linux
log_info "cryptominisat installed -> $PREFIX"
