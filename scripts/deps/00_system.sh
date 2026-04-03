#!/bin/bash
set -euo pipefail

if [[ "$(uname)" == "Linux" ]]; then
  dnf install -y help2man wget
else
  brew install wget
  brew uninstall mpfr gmp --ignore-dependencies
fi
