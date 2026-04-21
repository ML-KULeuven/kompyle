#!/bin/bash
set -euo pipefail

DEPS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DEPS_DIR/common.sh"

if [[ "$(uname)" == "Linux" ]]; then
  dnf install -y help2man wget ripgrep ninja-build graphviz
else
  brew install wget ripgrep ninja graphviz
  brew uninstall mpfr gmp --ignore-dependencies
fi
