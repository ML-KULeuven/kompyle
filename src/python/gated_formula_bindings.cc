// Copyright (c) 2026 Ibrahim El Kaddouri
// Licensed under apachev2

#include <iostream>

#include "nanobind/nanobind.h"

#include "python/bindings.h"
#include "kompyle/gated_formula.h"

namespace kmpyl {

namespace nb = nanobind;
using nb::literals::operator""_a;

void InitGatedFormulaBindings(nb::module_& m) {
  nb::class_<GatedFormula>(
      m, "GatedFormula",
      "Programmatic builder for BC-style gate formulas.\n\n"
      "A GatedFormula is a pure value: it records inputs, gates, and\n"
      "targets by string name. It holds no reference to any circuit and\n"
      "can be compiled into any number of circuits.\n\n"
      "Example\n"
      "~~~~~~~\n"
      "    gf = kompyle.GatedFormula()\n"
      "    gf.add_input('a')\n"
      "    gf.add_input('b')\n"
      "    gf.add_input('c')\n"
      "    gf.add_and('g1', ['a', 'b'])      # g1 := A   a   b\n"
      "    gf.add_and('g2', ['-c', 'b'])     # g2 := A  -c   b\n"
      "    gf.add_or ('g3', ['g1', '-g2'])   # g3 := O  g1 -g2\n"
      "    gf.add_target('g3')\n"
      "\n"
      "    circuit = kompyle.Circuit()\n"
      "    root = kompyle.compile_from_gates_formula_using_d4v2(circuit, gf)")
      .def(nb::init<>())
      .def("add_and", &GatedFormula::add_and, "gate"_a, "inputs"_a,
           "Append a gate: `output := AND of inputs`. Inputs may start "
           "with '-' for negation.")
      .def("add_or", &GatedFormula::add_or, "gate"_a, "inputs"_a,
           "Append a gate: `output := OR of inputs`. Inputs may start "
           "with '-' for negation.")
      .def("add_input", &GatedFormula::add_input, "name"_a,
           "Declare an input variable (BC-S1.2 'I' line).")
      .def("add_target", &GatedFormula::add_target, "token"_a,
           "Mark a literal as a target (BC-S1.2 'T' line). Token may "
           "start with '-' for negation.")
      .def("display",
           [](const GatedFormula& gf) { gf.display(std::cout); });
}

}  // namespace kmpyl
