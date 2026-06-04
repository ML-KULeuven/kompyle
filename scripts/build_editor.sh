#!/bin/bash
# building nvim from source due to glibc mismatch in almalinux base image
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/deps/common.sh"
enter_build_dir

log_step "editor: install build deps"
if [[ "$(uname)" == "Linux" ]]; then
  run_cmd dnf install -y clang-tools-extra readline-devel
else
  run_cmd brew install readline
fi

log_step "editor: clone neovim v0.11.7"
run_cmd git clone --depth 1 --branch v0.11.7 https://github.com/neovim/neovim.git
cd neovim

log_step "editor: build ($NPROC cores)"
run_cmd make CMAKE_BUILD_TYPE=Release

log_step "editor: install"
# run_cmd $SUDO make install
run_cmd make install

cd "$BUILD_DIR"
log_info "neovim installed"
