#!/bin/bash
set -euo pipefail

DEPS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DEPS_DIR/common.sh"

if command -v dnf &>/dev/null; then
  log_info "installing system packages via dnf"
  # run_cmd $SUDO dnf install -y help2man wget ripgrep ninja-build graphviz
  run_cmd dnf install -y help2man wget ripgrep ninja-build graphviz
elif command -v apt-get &>/dev/null; then
  log_info "installing system packages via apt-get"
  # run_cmd $SUDO apt-get install -y help2man wget ripgrep ninja-build graphviz
  run_cmd apt-get install -y help2man wget ripgrep ninja-build graphviz
elif command -v brew &>/dev/null; then
  log_info "installing system packages via brew"
  run_cmd brew install wget ripgrep ninja graphviz
  run_cmd brew uninstall mpfr gmp --ignore-dependencies || true
else
  log_error "no supported package manager found"
  log_error "  dnf     -> $(command -v dnf     2>/dev/null || echo 'not found')"
  log_error "  apt-get -> $(command -v apt-get 2>/dev/null || echo 'not found')"
  log_error "  brew    -> $(command -v brew    2>/dev/null || echo 'not found')"
  # exit 1
fi

log_info "system packages installed"
