// Copyright (c) 2026 Ibrahim El Kaddouri
// Licensed under apachev2

#include "kompyle/core.h"

#include <nanobind/nanobind.h>
#include <nanobind/stl/string.h>
#include <nanobind/stl/vector.h>
#include <nanobind/stl/pair.h>

namespace nb = nanobind;
using namespace nb::literals;

NB_MODULE(pkompyle, m) {
  m.def("compile_from_ganak",
      [](Circuit* circuit, const std::string& cnf_file) -> NodePtr {
        return compile_from_ganak(circuit, cnf_file);
      },
      "circuit"_a, "cnf_file"_a,
      "Compile a CNF file using Ganak and add the resulting"
      "nodes into an existing Circuit."
  );
  m.def("compile_from_ganak_with_arjun",
      [](Circuit* circuit, const std::string& cnf_file) -> NodePtr {
        return compile_from_ganak_with_arjun(circuit, cnf_file);
      },
      "circuit"_a, "cnf_file"_a,
      "Compile a CNF file using Ganak + Arjun "
      "and add the resulting nodes into an existing Circuit."
  );
}
