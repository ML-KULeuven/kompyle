#!/bin/bash
set -euo pipefail

if [[ "$(uname)" == "Linux" ]]; then
  dnf install -y help2man wget boost-devel ripgrep ninja-build graphviz
else
  brew install wget boost ripgrep ninja graphviz
  brew uninstall mpfr gmp --ignore-dependencies
fi
