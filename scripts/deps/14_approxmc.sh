#!/bin/bash
set -euo pipefail

DEPS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DEPS_DIR/common.sh"
enter_build_dir


log_info "cloning approxmc"
if [ ! -d approxmc/.git ]; then
  run_cmd git clone https://github.com/meelgroup/approxmc.git
fi
cd approxmc

log_info "checking out pinned commit"
run_cmd git checkout e1cd45156639c6ca794b14050d5ca546921e7455

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
run_cmd cmake --install . --config $BUILD_TYPE

cd "$BUILD_DIR"
run_cmd ldconfig_if_linux
log_info "approxmc installed -> $PREFIX"
