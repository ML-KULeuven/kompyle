#!/bin/bash
set -euo pipefail

DEPS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DEPS_DIR/common.sh"
enter_build_dir

log_info "downloading ensmallen 2.22.2"
run_cmd wget -O ensmallen-2.22.2.tar.gz https://github.com/mlpack/ensmallen/archive/refs/tags/2.22.2.tar.gz

log_info "extracting"
run_cmd tar xf ensmallen-2.22.2.tar.gz
cd ensmallen-2.22.2
mkdir -p build && cd build

log_info "configuring"
run_cmd cmake -DCMAKE_POLICY_VERSION_MINIMUM=3.5 -DCMAKE_INSTALL_PREFIX="${PREFIX}" ..

log_info "building ($NPROC cores)"
run_cmd cmake --build . -j$NPROC --config $BUILD_TYPE

log_info "installing"
# run_cmd $SUDO cmake --install . --config $BUILD_TYPE
run_cmd cmake --install . --config $BUILD_TYPE

cd "$BUILD_DIR"
log_info "ensmallen installed -> $PREFIX"
