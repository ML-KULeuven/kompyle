#!/bin/bash
set -euo pipefail

DEPS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DEPS_DIR/common.sh"
enter_build_dir

log_info "cloning cadical"
if [ ! -d cadical/.git ]; then
  run_cmd git clone https://github.com/meelgroup/cadical.git
fi
cd cadical

log_info "checking out pinned commit"
run_cmd git checkout 729939aba815b1837b1590279e66c61ed9d3092f

log_info "configuring"
run_cmd env CXXFLAGS="-fPIC" ./configure --competition

log_info "building ($NPROC cores)"
run_cmd make -j$NPROC

log_info "installing"
run_cmd mkdir -p "${PREFIX}/lib" "${PREFIX}/include/cadical"
run_cmd cp build/libcadical.a "${PREFIX}/lib/"
run_cmd cp src/cadical.hpp "${PREFIX}/include/cadical/"

cd "$BUILD_DIR"
run_cmd ldconfig_if_linux
log_info "cadical installed -> $PREFIX"
