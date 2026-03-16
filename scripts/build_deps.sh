#!/bin/bash
set -xe

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
make -j$(nproc)
$SUDO make install
cd ..

# macos
# wget https://zlib.net/fossils/zlib-1.3.1.tar.gz
# tar xzvf zlib-1.3.1.tar.gz
# cd zlib-1.3.1
# ./configure --static
# make -j8
# sudo make install
# cd ..

[[ "$(uname)" == "Linux" ]] && ldconfig

# mpfr version 4.2.1
wget -q https://ftp.gnu.org/gnu/mpfr/mpfr-4.2.1.tar.xz
tar xJf mpfr-4.2.1.tar.xz
cd mpfr-4.2.1
./configure --enable-cxx --enable-shared
make -j$(nproc)
$SUDO make install
cd ..

[[ "$(uname)" == "Linux" ]] && ldconfig

wget -q \
  https://github.com/flintlib/flint/releases/download/v3.2.0-rc1/flint-3.2.0-rc1.tar.gz
tar xzf flint-3.2.0-rc1.tar.gz
cd flint-3.2.0-rc1
./configure --enable-shared
make -j$(nproc)
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
cmake --build .  -j$(nproc)  --config $BUILD_TYPE -v
$SUDO cmake --install .  --config $BUILD_TYPE -v
cd ../..

wget -q \
  https://sourceforge.net/projects/arma/files/armadillo-14.0.2.tar.xz
tar xf armadillo-14.0.2.tar.xz
cd armadillo-14.0.2
./configure
make -j$(nproc)
$SUDO make install
cd ..

wget -q \
  https://github.com/mlpack/ensmallen/archive/refs/tags/2.22.2.tar.gz
tar xf 2.22.2.tar.gz
cd ensmallen-2.22.2 && mkdir build && cd build
cmake -DCMAKE_POLICY_VERSION_MINIMUM=3.5 ..
cmake --build . -j$(nproc) --config $BUILD_TYPE -v
$SUDO cmake --install .  --config $BUILD_TYPE -v
cd ../..

git clone --depth=1 https://github.com/meelgroup/cadical.git
cd cadical
CXXFLAGS="-fPIC" ./configure --competition
make -j$(nproc)
$SUDO cp build/libcadical.a /usr/local/lib/
cd ..

git clone --depth=1 https://github.com/meelgroup/cadiback.git
cd cadiback
CXX=c++ ./configure 
make -j$(nproc)
$SUDO cp libcadiback.a /usr/local/lib/
cd ..

[[ "$(uname)" == "Linux" ]] && ldconfig

git clone --depth 1 https://github.com/meelgroup/breakid.git
cd breakid && mkdir build && cd build
cmake \
  -DCMAKE_BUILD_TYPE=$BUILD_TYPE \
  -DENABLE_TESTING=OFF \
  -DSTATICCOMPILE=OFF \
  ..
cmake --build . -j$(nproc) --config $BUILD_TYPE -v
$SUDO cmake --install .
cd ../../

[[ "$(uname)" == "Linux" ]] && ldconfig

git clone --depth 1 https://github.com/msoos/cryptominisat.git
cd cryptominisat && mkdir build && cd build
cmake \
  -DCMAKE_BUILD_TYPE=$BUILD_TYPE \
  -DENABLE_TESTING=OFF \
  -DSTATICCOMPILE=OFF \
  ..
cmake --build . -j$(nproc) --config $BUILD_TYPE -v
$SUDO cmake --install .
cd ../../

[[ "$(uname)" == "Linux" ]] && ldconfig

git clone --depth 1 https://github.com/meelgroup/SBVA.git
cd SBVA && mkdir build && cd build
cmake \
  -DCMAKE_BUILD_TYPE=$BUILD_TYPE \
  -DENABLE_TESTING=OFF \
  -DSTATICCOMPILE=OFF \
  ..
cmake --build . -j$(nproc) --config $BUILD_TYPE -v
$SUDO cmake --install .
cd ../../

[[ "$(uname)" == "Linux" ]] && ldconfig

git clone --depth 1 https://github.com/mlpack/mlpack.git
cd mlpack && mkdir build && cd build
cmake \
  -DCMAKE_BUILD_TYPE=$BUILD_TYPE \
  -DBUILD_SHARED_LIBS=ON \
  -DBUILD_CLI_EXECUTABLES=OFF \
  ..
cmake --build . -j$(nproc) --config $BUILD_TYPE -v
$SUDO cmake --install .  --config $BUILD_TYPE -v
cd ../../

[[ "$(uname)" == "Linux" ]] && ldconfig

git clone --depth 1 https://github.com/meelgroup/arjun.git
cd arjun && mkdir build && cd build
cmake \
  -DCMAKE_BUILD_TYPE=$BUILD_TYPE \
  -DENABLE_TESTING=OFF \
  -DSTATICCOMPILE=OFF \
  ..
cmake --build . -j$(nproc)  --config $BUILD_TYPE -v
$SUDO cmake --install .  --config $BUILD_TYPE -v
cd ../../

[[ "$(uname)" == "Linux" ]] && ldconfig

git clone --depth 1 https://github.com/meelgroup/approxmc.git
cd approxmc && mkdir build && cd build
cmake \
  -DCMAKE_BUILD_TYPE=$BUILD_TYPE \
  -DENABLE_TESTING=OFF \
  -DSTATICCOMPILE=OFF \
  ..
cmake --build . -j$(nproc)  --config $BUILD_TYPE -v
$SUDO cmake --install .  --config $BUILD_TYPE -v
cd ../../

[[ "$(uname)" == "Linux" ]] && ldconfig

git clone --depth 1 https://github.com/IbrahimElk/ganak.git
cd ganak && mkdir build && cd build
cmake \
  -DCMAKE_BUILD_TYPE=$BUILD_TYPE \
  -DENABLE_TESTING=OFF \
  -DSTATICCOMPILE=OFF \
  ..
cmake --build . -j$(nproc)  --config $BUILD_TYPE -v
$SUDO cmake --install .  --config $BUILD_TYPE -v
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
