#!/bin/bash
set -euo pipefail

DEPS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DEPS_DIR/common.sh"
enter_build_dir

log_info "cloning mlpack 4.7.0"
if [ ! -d mlpack/.git ]; then
  run_cmd git clone --depth=1 --branch 4.7.0 https://github.com/mlpack/mlpack.git
fi

cd mlpack
mkdir -p build && cd build

log_info "configuring"
run_cmd cmake \
  -DCMAKE_BUILD_TYPE=$BUILD_TYPE \
  -DCMAKE_INSTALL_PREFIX="${PREFIX}" \
  -DBUILD_SHARED_LIBS=ON \
  -DBUILD_CLI_EXECUTABLES=OFF \
  ..

log_info "building ($NPROC cores)"
run_cmd cmake --build . -j$NPROC --config $BUILD_TYPE

log_info "installing"
# run_cmd $SUDO cmake --install . --config $BUILD_TYPE
run_cmd cmake --install . --config $BUILD_TYPE

cd "$BUILD_DIR"
run_cmd ldconfig_if_linux
log_info "mlpack installed -> $PREFIX"
