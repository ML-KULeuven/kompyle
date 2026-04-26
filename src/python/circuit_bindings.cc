// Copyright (c) 2026 Ibrahim El Kaddouri
// Licensed under apachev2

#include "nanobind/nanobind.h"

#include "python/bindings.h"
#include "kompyle/kcircuit.h"

namespace kmpyl {

namespace nb = nanobind;

void InitCircuitBindings(nb::module_& m) {
  nb::class_<Circuit, klay::Circuit>(
      m, "Circuit",
      "A klay.Circuit that also carries a string -> integer variable-name "
      "map. Use this whenever you want to compile BC files or "
      "GatedFormulas, it guarantees that the same variable name resolves "
      "to the same integer across every formula compiled into the same "
      "circuit.")
      .def(nb::init<>())
      .def("nb_vars", &Circuit::nb_vars,
           "Number of distinct variable names registered so far.");
}

}  // namespace kmpyl
