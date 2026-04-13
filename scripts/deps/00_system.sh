#!/bin/bash
set -euo pipefail

if [[ "$(uname)" == "Linux" ]]; then
  dnf install -y help2man wget boost-devel ripgrep ninja-build
else
  brew install wget boost ripgrep ninja
  brew uninstall mpfr gmp --ignore-dependencies
fi
