# building nvim from source due to glibc mismatch in almalinux base image

if [[ "$(uname)" == "Linux" ]]; then
  dnf install -y clang-tools-extra readline-devel
else
  brew install readline
fi

git clone --depth 1 --branch v0.11.7 https://github.com/neovim/neovim.git /tmp/neovim
cd /tmp/neovim
make CMAKE_BUILD_TYPE=Release
make install
rm -rf /tmp/neovim

exit 0
