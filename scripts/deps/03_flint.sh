#!/bin/bash
set -euo pipefail

DEPS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DEPS_DIR/common.sh"
enter_build_dir

log_info "downloading flint 3.2.0-rc1"
run_cmd wget https://github.com/flintlib/flint/releases/download/v3.2.0-rc1/flint-3.2.0-rc1.tar.gz

log_info "extracting"
run_cmd tar xzf flint-3.2.0-rc1.tar.gz
cd flint-3.2.0-rc1

log_info "configuring"
run_cmd ./configure --enable-shared --prefix="${PREFIX}"

log_info "building ($NPROC cores)"
run_cmd make -j$NPROC

log_info "installing"
run_cmd make install

cd "$BUILD_DIR"
run_cmd ldconfig_if_linux
log_info "flint installed -> $PREFIX"
