#!/bin/bash
set -euo pipefail

DEPS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DEPS_DIR/common.sh"
enter_build_dir

log_info "cloning cadiback"
if [ ! -d cadiback/.git ]; then
  run_cmd git clone https://github.com/meelgroup/cadiback.git
fi
cd cadiback

log_info "checking out pinned commit"
run_cmd git checkout a44d5a94c8b8c2c4c8c77116ce80d2bb3a974252

log_info "configuring"
run_cmd env CXX=c++ ./configure

log_info "building ($NPROC cores)"
run_cmd make -j$NPROC

log_info "installing"
# run_cmd $SUDO mkdir -p "${PREFIX}/lib"
# run_cmd $SUDO cp libcadiback.a "${PREFIX}/lib/"
run_cmd mkdir -p "${PREFIX}/lib"
run_cmd cp libcadiback.a "${PREFIX}/lib/"

cd "$BUILD_DIR"
run_cmd ldconfig_if_linux
log_info "cadiback installed -> $PREFIX"
