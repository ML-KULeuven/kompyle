#!/bin/bash
set -euo pipefail

DEPS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DEPS_DIR/common.sh"

wget -q https://github.com/USCiLab/cereal/archive/v1.3.2.tar.gz
tar xf v1.3.2.tar.gz

# patch for modern compilers
if sed --version >/dev/null 2>&1; then
  sed -i 's|::template apply|::apply|' cereal-1.3.2/include/cereal/types/tuple.hpp
else
  sed -i '' 's|::template apply|::apply|' cereal-1.3.2/include/cereal/types/tuple.hpp
fi

cd cereal-1.3.2 && mkdir build && cd build
cmake -DJUST_INSTALL_CEREAL=ON ..
cmake --build . -j$NPROC --config $BUILD_TYPE
$SUDO cmake --install . --config $BUILD_TYPE
cd ../..
cleanup cereal-1.3.2 v1.3.2.tar.gz
