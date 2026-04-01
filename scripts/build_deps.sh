#!/bin/bash
set -euo pipefail

# ============================================================
# system-packages
# ============================================================
if [[ "$(uname)" == "Linux" ]]; then
  # gmp-devel version 6.2.1 or later is required but not available.
  # mpfr-devel version 4.1.0 or later is required but not available.
  # both built form source
  dnf install -y help2man wget
else
  brew install wget
  brew uninstall mpfr gmp --ignore-dependencies
fi

if [[ "$(uname)" == "Linux" ]]; then
  NPROC=$(nproc)
else
  NPROC=$(sysctl -n hw.ncpu)
fi
# ============================================================
# dependencies
# ============================================================
BUILD_TYPE="Release"

SUDO=""
[[ "$(uname)" == "Darwin" ]] && SUDO="sudo"

# gmp version 6.2.1
wget -q https://ftp.gnu.org/gnu/gmp/gmp-6.3.0.tar.xz
tar xf gmp-6.3.0.tar.xz
cd gmp-6.3.0
./configure --enable-cxx --enable-shared
make -j$NPROC
$SUDO make install
cd ..

[[ "$(uname)" == "Linux" ]] && ldconfig

# mpfr version 4.2.1
wget -q https://ftp.gnu.org/gnu/mpfr/mpfr-4.2.1.tar.xz
tar xJf mpfr-4.2.1.tar.xz
cd mpfr-4.2.1
./configure --enable-cxx --enable-shared
make -j$NPROC
$SUDO make install
cd ..

[[ "$(uname)" == "Linux" ]] && ldconfig

wget -q \
  https://github.com/flintlib/flint/releases/download/v3.2.0-rc1/flint-3.2.0-rc1.tar.gz
tar xzf flint-3.2.0-rc1.tar.gz
cd flint-3.2.0-rc1
./configure --enable-shared
make -j$NPROC
$SUDO make install
cd ..

[[ "$(uname)" == "Linux" ]] && ldconfig

wget -q https://github.com/USCiLab/cereal/archive/v1.3.2.tar.gz
tar xf v1.3.2.tar.gz
if sed --version >/dev/null 2>&1; then
    # GNU sed (Linux)
    sed -i 's|::template apply|::apply|' cereal-1.3.2/include/cereal/types/tuple.hpp
else
    # BSD sed (macOS)
    sed -i '' 's|::template apply|::apply|' cereal-1.3.2/include/cereal/types/tuple.hpp
fi
cd cereal-1.3.2 && mkdir build && cd build
cmake -DJUST_INSTALL_CEREAL=ON ..
cmake --build .  -j$NPROC  --config $BUILD_TYPE -v
$SUDO cmake --install .  --config $BUILD_TYPE -v
cd ../..

wget -q \
  https://sourceforge.net/projects/arma/files/armadillo-14.0.2.tar.xz
tar xf armadillo-14.0.2.tar.xz
cd armadillo-14.0.2
./configure
make -j$NPROC
$SUDO make install
cd ..

wget -q \
  https://github.com/mlpack/ensmallen/archive/refs/tags/2.22.2.tar.gz
tar xf 2.22.2.tar.gz
cd ensmallen-2.22.2 && mkdir build && cd build
cmake -DCMAKE_POLICY_VERSION_MINIMUM=3.5 ..
cmake --build . -j$NPROC --config $BUILD_TYPE -v
$SUDO cmake --install .  --config $BUILD_TYPE -v
cd ../..

[[ "$(uname)" == "Linux" ]] && ldconfig

git clone --depth=1 --branch 4.7.0 https://github.com/mlpack/mlpack.git
cd mlpack && mkdir build && cd build
cmake \
  -DCMAKE_BUILD_TYPE=$BUILD_TYPE \
  -DBUILD_SHARED_LIBS=ON \
  -DBUILD_CLI_EXECUTABLES=OFF \
  ..
cmake --build . -j$NPROC --config $BUILD_TYPE -v
$SUDO cmake --install .  --config $BUILD_TYPE -v
cd ../../

[[ "$(uname)" == "Linux" ]] && ldconfig

# NOTE(Ibrahim):
# not tags yet in this repo, so specifying commit hash
git clone \
  --revision=729939aba815b1837b1590279e66c61ed9d3092f \
  --depth=1 https://github.com/meelgroup/cadical.git
cd cadical
CXXFLAGS="-fPIC" ./configure --competition
make -j$NPROC
$SUDO cp build/libcadical.a /usr/local/lib/
cd ..

git clone \
  --revision=a44d5a94c8b8c2c4c8c77116ce80d2bb3a974252 \
  --depth=1 https://github.com/meelgroup/cadiback
cd cadiback
CXX=c++ ./configure 
make -j$NPROC
$SUDO cp libcadiback.a /usr/local/lib/
cd ..

[[ "$(uname)" == "Linux" ]] && ldconfig

git clone \
  --revision=101bc75aecbca22fc288a870c105889807384ffd \
  --depth=1 https://github.com/meelgroup/breakid
cd breakid && mkdir build && cd build
cmake \
  -DCMAKE_BUILD_TYPE=$BUILD_TYPE \
  -DENABLE_TESTING=OFF \
  -DSTATICCOMPILE=OFF \
  ..
cmake --build . -j$NPROC --config $BUILD_TYPE -v
$SUDO cmake --install .
cd ../../

[[ "$(uname)" == "Linux" ]] && ldconfig

git clone --depth=1 https://github.com/msoos/cryptominisat.git
cd cryptominisat && mkdir build && cd build
cmake \
  -DCMAKE_BUILD_TYPE=$BUILD_TYPE \
  -DENABLE_TESTING=OFF \
  -DSTATICCOMPILE=OFF \
  ..
cmake --build . -j$NPROC --config $BUILD_TYPE -v
$SUDO cmake --install .
cd ../../

[[ "$(uname)" == "Linux" ]] && ldconfig

git clone \
  --revision=52c1835773cb97edab25dfaa7c27d23ba1e5b71e \
  --depth=1 https://github.com/meelgroup/SBVA
cd SBVA && mkdir build && cd build
cmake \
  -DCMAKE_BUILD_TYPE=$BUILD_TYPE \
  -DENABLE_TESTING=OFF \
  -DSTATICCOMPILE=OFF \
  ..
cmake --build . -j$NPROC --config $BUILD_TYPE -v
$SUDO cmake --install .
cd ../../

[[ "$(uname)" == "Linux" ]] && ldconfig

git clone \
  --revision=bbdda468af0c70ab1cb442639a0800d567e0e1a2 \
  --depth=1 https://github.com/meelgroup/arjun
cd arjun && mkdir build && cd build
cmake \
  -DCMAKE_BUILD_TYPE=$BUILD_TYPE \
  -DENABLE_TESTING=OFF \
  -DSTATICCOMPILE=OFF \
  ..
cmake --build . -j$NPROC  --config $BUILD_TYPE -v
$SUDO cmake --install .  --config $BUILD_TYPE -v
cd ../../

[[ "$(uname)" == "Linux" ]] && ldconfig

git clone \
  --revision=e1cd45156639c6ca794b14050d5ca546921e7455 \
  --depth=1 https://github.com/meelgroup/approxmc
cd approxmc && mkdir build && cd build
cmake \
  -DCMAKE_BUILD_TYPE=$BUILD_TYPE \
  -DENABLE_TESTING=OFF \
  -DSTATICCOMPILE=OFF \
  ..
cmake --build . -j$NPROC  --config $BUILD_TYPE -v
$SUDO cmake --install .  --config $BUILD_TYPE -v
cd ../../

[[ "$(uname)" == "Linux" ]] && ldconfig

git clone \
  --revision=4b6037d2efbbcbb8ae30f4b2d670bfaeff4a284d \
  --depth=1 https://github.com/IbrahimElk/ganak
cd ganak && mkdir build && cd build
cmake \
  -DCMAKE_BUILD_TYPE=$BUILD_TYPE \
  -DENABLE_TESTING=OFF \
  -DSTATICCOMPILE=OFF \
  ..
cmake --build . -j$NPROC  --config $BUILD_TYPE -v
$SUDO cmake --install .  --config $BUILD_TYPE -v
cd ../../

[[ "$(uname)" == "Linux" ]] && ldconfig

git clone --depth=1 https://github.com/IbrahimElk/sdd
cd sdd && mkdir build && cd build
cmake \
  -DCMAKE_BUILD_TYPE=$BUILD_TYPE \
  ..
cmake --build . -j$NPROC  -v
$SUDO cmake --install .  -v
cd ../../

[[ "$(uname)" == "Linux" ]] && ldconfig
exit 0

# # ============================================================
# # klay
# # ============================================================
#
# git clone https://github.com/IbrahimElk/klay.git
# cd klay
# git checkout rel-separation-of-concerns
# cmake -S . -B build
# cmake --build build -j$(nproc)
# cmake --install build
# cd ..
#
# [[ "$(uname)" == "Linux" ]] && ldconfig
