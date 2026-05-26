#!/usr/bin/env bash
# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2
#
# Shared helpers sourced by both local and SLURM scripts.
# Defines:
#   benchmark_dir        repo's benchmark/ on the local machine
#   die <msg>            print to stderr and exit 1
#   require_var <name>   fail unless the named env var is set
#   require_file <path>  fail unless the path exists
#   log <msg>            timestamped stderr line

_lib_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
benchmark_dir="$(cd "${_lib_dir}/../.." && pwd)"
unset _lib_dir

die() {
    echo "ERROR: $*" >&2
    exit 1
}

log() {
    printf '[%s] %s\n' "$(date '+%H:%M:%S')" "$*" >&2
}

require_var() {
    local name="$1"
    [[ -n "${!name:-}" ]] || die "required env var ${name} is unset"
}

require_file() {
    [[ -f "$1" ]] || die "required file not found: $1"
}
