#!/bin/bash
set -euo pipefail

DEPS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DEPS_DIR/common.sh"
enter_build_dir

log_info "downloading armadillo 14.0.2"
run_cmd wget https://sourceforge.net/projects/arma/files/armadillo-14.0.2.tar.xz

log_info "extracting"
run_cmd tar xf armadillo-14.0.2.tar.xz
cd armadillo-14.0.2

log_info "configuring"
run_cmd ./configure "-DCMAKE_INSTALL_PREFIX=${PREFIX}" "-DCMAKE_BUILD_TYPE=${BUILD_TYPE}"

log_info "building ($NPROC cores)"
run_cmd make -j$NPROC

log_info "installing"
# run_cmd $SUDO make install
run_cmd make install

cd "$BUILD_DIR"
run_cmd ldconfig_if_linux
log_info "armadillo installed -> $PREFIX"
