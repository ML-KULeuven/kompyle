#!/bin/bash
set -euo pipefail

DEPS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DEPS_DIR/common.sh"
enter_build_dir

log_info "downloading gmp 6.3.0"
run_cmd wget https://ftp.gnu.org/gnu/gmp/gmp-6.3.0.tar.xz

log_info "extracting"
run_cmd tar xf gmp-6.3.0.tar.xz
cd gmp-6.3.0

log_info "configuring"
# run_cmd ./configure --enable-cxx --enable-shared --prefix="${PREFIX}"
run_cmd env CFLAGS="-std=gnu17 ${CFLAGS:-}" \
  ./configure --enable-cxx --enable-shared --prefix="${PREFIX}"


log_info "building ($NPROC cores)"
run_cmd make -j$NPROC

log_info "installing"
# run_cmd $SUDO make install
run_cmd make install

cd "$BUILD_DIR"
run_cmd ldconfig_if_linux
log_info "gmp installed -> $PREFIX"
