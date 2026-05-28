#!/bin/bash
set -euo pipefail

DEPS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DEPS_DIR/common.sh"
enter_build_dir

log_info "cloning ganak"
if [ ! -d ganak/.git ]; then
  run_cmd git clone https://github.com/Ibrahimelk/ganak.git
fi
cd ganak

log_info "checking out pinned commit"
run_cmd git checkout 4b6037d2efbbcbb8ae30f4b2d670bfaeff4a284d

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
log_info "ganak installed -> $PREFIX"
