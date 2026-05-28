#!/bin/bash
set -euo pipefail

DEPS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DEPS_DIR/common.sh"
enter_build_dir

log_info "downloading boost 1.90.0"
run_cmd wget https://archives.boost.io/release/1.90.0/source/boost_1_90_0.tar.gz

log_info "extracting"
run_cmd tar xf boost_1_90_0.tar.gz
cd boost_1_90_0

log_info "bootstrapping"
run_cmd ./bootstrap.sh --with-libraries=program_options --prefix="${PREFIX}"

log_info "building and installing ($NPROC cores)"
if [[ "$(uname)" == "Darwin" ]]; then
  # run_cmd $SUDO ./b2 -j$NPROC install --prefix="${PREFIX}" \
  run_cmd ./b2 -j$NPROC install --prefix="${PREFIX}" \
    cxxflags="-mmacosx-version-min=11.0" \
    linkflags="-mmacosx-version-min=11.0"
else
  # run_cmd $SUDO ./b2 -j$NPROC install --prefix="${PREFIX}"
  run_cmd ./b2 -j$NPROC install --prefix="${PREFIX}"
fi

cd "$BUILD_DIR"
run_cmd ldconfig_if_linux
log_info "boost installed -> $PREFIX"
