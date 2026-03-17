#!/bin/bash
set -e

check_lib() {
  local name="$1"; local header="$2"; local lib="$3"
  echo -n "checking $name ... "
  [[ -f "$header" ]] || { echo "MISSING header: $header"; exit 1; }
  [[ -f "$lib"    ]] || { echo "MISSING lib: $lib";    exit 1; }
  echo "ok"
}

check_bin() {
  local name="$1"; local bin="$2"
  echo -n "checking $name ... "
  [[ -f "$bin" ]] || { echo "MISSING: $bin"; exit 1; }
  echo "ok"
}

P=/usr/local

check_lib  "gmp"            "$P/include/gmp.h"                          "$P/lib/libgmp.dylib"
check_lib  "mpfr"           "$P/include/mpfr.h"                         "$P/lib/libmpfr.dylib"
check_lib  "flint"          "$P/include/flint/flint.h"                  "$P/lib/libflint.dylib"
check_lib  "cereal"         "$P/include/cereal/cereal.hpp"              ""
check_lib  "armadillo"      "$P/include/armadillo"                      "$P/lib/libarmadillo.dylib"
check_lib  "ensmallen"      "$P/include/ensmallen.hpp"                  ""
check_lib  "cryptominisat5" "$P/include/cryptominisat5/cryptominisat.h" "$P/lib/libcryptominisat5.dylib"
check_lib  "arjun"          "$P/include/arjun/arjun.h"                  "$P/lib/libarjun.dylib"
check_lib  "ganak"          "$P/include/ganak/ganak.hpp"                "$P/lib/libganak.dylib"
check_lib  "approxmc"       "$P/include/approxmc/approxmc.h"            "$P/lib/libapproxmc.dylib"
check_lib  "breakid"        "$P/include/breakid/breakid.hpp"            "$P/lib/libbreakid.dylib"
check_lib  "sbva"           "$P/include/sbva/sbva.h"                    "$P/lib/libsbva.dylib"
check_lib  "mlpack"         "$P/include/mlpack/mlpack.hpp"              "$P/lib/libmlpack.dylib"

check_lib  "cadical"        ""  "$P/lib/libcadical.a"
check_lib  "cadiback"       ""  "$P/lib/libcadiback.a"

echo "all dependencies validated :)"
