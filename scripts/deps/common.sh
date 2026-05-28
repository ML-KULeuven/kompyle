#!/bin/bash

# --------------------------------------------------------------------
# install prefix
#   system-wide:  PREFIX="/usr/local"
#   user:         PREFIX="$HOME/.local"
#   HPC:          PREFIX="${VSC_SCRATCH}/install"
# --------------------------------------------------------------------
export PREFIX="${PREFIX:-/usr/local}"
export BUILD_TYPE="${BUILD_TYPE:-Release}"

# --------------------------------------------------------------------
# scratch directory for tarballs and out-of-tree builds.
# kept OUT of wherever the user invoked the build script from.
#   /usr/* or /opt/*   -> /tmp/kompyle-deps
#   $HOME/*            -> $XDG_CACHE_HOME/kompyle-deps (i.e. ~/.cache)
#   anything else      -> <dirname of prefix>/kompyle-deps
# override with BUILD_DIR=/path env var if you need to.
# --------------------------------------------------------------------
if [[ -z "${BUILD_DIR:-}" ]]; then
  if [[ "$PREFIX" == /usr* || "$PREFIX" == /opt* ]]; then
    export BUILD_DIR="/tmp/kompyle-deps"
  elif [[ -n "${HOME:-}" && "$PREFIX" == "$HOME"* ]]; then
    export BUILD_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/kompyle-deps"
  else
    export BUILD_DIR="$(dirname "$PREFIX")/kompyle-deps"
  fi
fi

# # --------------------------------------------------------------------
# # sudo (empty when already root)
# # --------------------------------------------------------------------
# if [ -z "${SUDO+x}" ]; then
#   [ "$(id -u)" = "0" ] && export SUDO="" || export SUDO="sudo"
# fi

# --------------------------------------------------------------------
# parallelism
# --------------------------------------------------------------------
export NPROC
if [[ "$(uname)" == "Linux" ]]; then
  NPROC=$(nproc)
else
  NPROC=$(sysctl -n hw.ncpu)
fi

# --------------------------------------------------------------------
# make PREFIX visible to cmake, pkg-config and the linker
# --------------------------------------------------------------------
export CMAKE_INSTALL_PREFIX="${PREFIX}"
export PKG_CONFIG_PATH="${PREFIX}/lib/pkgconfig:${PKG_CONFIG_PATH:-}"
export LD_LIBRARY_PATH="${PREFIX}/lib:${LD_LIBRARY_PATH:-}"
export PATH="${PREFIX}/bin:${PATH}"

# --------------------------------------------------------------------
# logging colours (docker-style: my lines in blue, tool output in gray,
# errors in red). auto-disabled when not on a TTY or NO_COLOR is set.
# --------------------------------------------------------------------
if [[ -t 1 && -z "${NO_COLOR:-}" ]]; then
  BLUE='\033[1;34m'
  GRAY='\033[90m'
  RED='\033[1;31m'
  RESET='\033[0m'
else
  BLUE=''; GRAY=''; RED=''; RESET=''
fi

log_info()  { printf "${BLUE}[INFO]  %s${RESET}  %s\n"   "$(date '+%H:%M:%S')" "$*"; }
log_step()  { printf "\n${BLUE}[STEP]  %s${RESET}  %s\n" "$(date '+%H:%M:%S')" "$*"; }
log_error() { printf "${RED}[ERROR] %s${RESET}  %s\n"    "$(date '+%H:%M:%S')" "$*" >&2; }

# --------------------------------------------------------------------
# run a command.
#   VERBOSE=0 (default)
#     stdout+stderr captured. on success: nothing printed.
#     on failure: prints the command, the last 40 lines of output (in
#     gray), and the path to the full log so you can inspect it.
#   VERBOSE=1
#     output streamed live, each line prefixed with a gray "│" so it
#     visually nests under the [STEP] line above it.
# --------------------------------------------------------------------
run_cmd() {
  if [[ "${VERBOSE:-0}" == "1" ]]; then
    "$@" 2>&1 | while IFS= read -r line; do
      printf "${GRAY}  │ %s${RESET}\n" "$line"
    done
    return "${PIPESTATUS[0]}"
  fi

  local log rc=0
  log="$(mktemp -t kompyle-deps.XXXXXX.log)"
  "$@" &>"$log" || rc=$?
  if (( rc != 0 )); then
    log_error "command failed (exit $rc): $*"
    log_error "last 40 lines of output:"
    tail -n 40 "$log" | while IFS= read -r line; do
      printf "${GRAY}  │ %s${RESET}\n" "$line" >&2
    done
    log_error "full log kept at: $log"
    return "$rc"
  fi
  rm -f "$log"
}

# --------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------
ldconfig_if_linux() {
  [[ "$(uname)" == "Linux" ]] && ldconfig
  return 0
}

cleanup() {
  rm -rf "$@"
}

# create BUILD_DIR if needed and cd into it.
# call once at the top of every dep script so wget/git/tar all land
# in the same scratch tree rather than in $PWD.
enter_build_dir() {
  mkdir -p "$BUILD_DIR"
  cd "$BUILD_DIR"
}
