#!/bin/bash
set -euo pipefail

DEPS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DEPS_DIR/common.sh"
enter_build_dir

log_info "cloning arjun"
if [ ! -d arjun/.git ]; then
  run_cmd git clone https://github.com/meelgroup/arjun.git
fi
cd arjun

log_info "checking out pinned commit"
run_cmd git checkout bbdda468af0c70ab1cb442639a0800d567e0e1a2

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
log_info "arjun installed -> $PREFIX"
