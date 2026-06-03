#!/bin/bash
set -euo pipefail

DEPS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DEPS_DIR/common.sh"
enter_build_dir

log_info "downloading cereal 1.3.2"
run_cmd wget -O cereal-1.3.2.tar.gz https://github.com/USCiLab/cereal/archive/v1.3.2.tar.gz

log_info "extracting"
run_cmd tar xf cereal-1.3.2.tar.gz

log_info "patching for modern compilers"
if sed --version >/dev/null 2>&1; then
  run_cmd sed -i 's|::template apply|::apply|' cereal-1.3.2/include/cereal/types/tuple.hpp
else
  run_cmd sed -i '' 's|::template apply|::apply|' cereal-1.3.2/include/cereal/types/tuple.hpp
fi

cd cereal-1.3.2
mkdir -p build && cd build

log_info "configuring"
run_cmd cmake -DJUST_INSTALL_CEREAL=ON -DCMAKE_INSTALL_PREFIX="${PREFIX}" ..

log_info "building ($NPROC cores)"
run_cmd cmake --build . -j$NPROC --config $BUILD_TYPE

log_info "installing"
run_cmd cmake --install . --config $BUILD_TYPE

cd "$BUILD_DIR"
log_info "cereal installed -> $PREFIX"
