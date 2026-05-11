#!/bin/bash
set -euo pipefail

DEPS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DEPS_DIR/common.sh"

wget -q https://archives.boost.io/release/1.90.0/source/boost_1_90_0.tar.gz
tar xf boost_1_90_0.tar.gz
cd boost_1_90_0
./bootstrap.sh --with-libraries=program_options --prefix="${PREFIX}"

if [[ "$(uname)" == "Darwin" ]]; then
  $SUDO ./b2 -j$NPROC install --prefix="${PREFIX}" \
    cxxflags="-mmacosx-version-min=11.0" \
    linkflags="-mmacosx-version-min=11.0"
else
  $SUDO ./b2 -j$NPROC install --prefix="${PREFIX}"
fi
cd ..
# cleanup boost_1_90_0 boost_1_90_0.tar.gz
ldconfig_if_linux

