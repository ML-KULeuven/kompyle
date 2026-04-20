// Copyright (c) 2026 Ibrahim El Kaddouri
// Licensed under apachev2

#include "kompyle/core.h"

#include <nanobind/nanobind.h>
#include <nanobind/stl/string.h>
#include <nanobind/stl/vector.h>
#include <nanobind/stl/pair.h>

#include <Python.h>

namespace nb = nanobind;
using namespace nb::literals;

namespace kmpyl {

NB_MODULE(pkompyle, m) {
  nb::module_::import_("klay");

  // ---------------------------------------------------------------------
  // kompyle.Circuit
  // ---------------------------------------------------------------------
  nb::class_<Circuit, klay::Circuit>(m, "Circuit",
      "A klay.Circuit that also carries a string -> integer variable-name "
      "map. Use this whenever you want to compile BC files or "
      "GatedFormulas, it guarantees that the same variable name resolves "
      "to the same integer across every formula compiled into the same "
      "circuit.")
    .def(nb::init<>())
    .def("var_for_name", &Circuit::var_for_name, "name"_a,
         "Get-or-create the integer var id for a name. Calling twice with "
         "the same name returns the same id.")
    .def("nb_vars", &Circuit::nb_vars,
         "Number of distinct variable names registered so far.");

  // ---------------------------------------------------------------------
  // kompyle.GatedFormula
  // ---------------------------------------------------------------------
  nb::class_<GatedFormula>(m, "GatedFormula",
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
      "    gf.add_and('g1', ['a', 'b'])      # g1 := a AND b\n"
      "    gf.add_and('g2', ['-c', 'b'])     # g2 := -c AND b\n"
      "    gf.add_or ('g3', ['g1', '-g2'])   # g3 := g1 OR -g2\n"
      "    gf.add_target('g3')\n"
      "\n"
      "    circuit = kompyle.Circuit()\n"
      "    root = kompyle.compile_from_gates_formula_using_d4v2(circuit, gf)")
    .def(nb::init<>())
    .def("add_and",    &GatedFormula::add_and,    "gate"_a, "inputs"_a,
         "Append a gate: `output := AND of inputs`. Inputs may start with "
         "'-' for negation.")
    .def("add_or",     &GatedFormula::add_or,     "gate"_a, "inputs"_a,
         "Append a gate: `output := OR of inputs`. Inputs may start with "
         "'-' for negation.")
    .def("add_input",  &GatedFormula::add_input,  "name"_a,
         "Declare an input variable (BC-S1.2 'I' line).")
    .def("add_target", &GatedFormula::add_target, "token"_a,
         "Mark a literal as a target (BC-S1.2 'T' line). Token may start "
         "with '-' for negation.")
    .def("display", [](const GatedFormula& gf) {
         gf.display(std::cout);
    });

  // ---------------------------------------------------------------------
  // Compile entry points.
  // ---------------------------------------------------------------------


  m.def("compile_from_cnf_using_ganak",
        [](Circuit* circuit, const std::string& cnf_file) -> klay::NodePtr {
          return compile_from_cnf_using_ganak(circuit, cnf_file);
        },
        "circuit"_a, "cnf_file"_a,
        "Compile a CNF file using Ganak and add the resulting nodes into "
        "an existing Circuit.");

  m.def("compile_from_cnf_using_ganakarjun",
        [](Circuit* circuit, const std::string& cnf_file) -> klay::NodePtr {
          return compile_from_cnf_using_ganakarjun(circuit, cnf_file);
        },
        "circuit"_a, "cnf_file"_a,
        "Compile a CNF file using Ganak + Arjun and add the resulting "
        "nodes into an existing Circuit.");

  m.def("compile_from_cnf_using_sdd",
        [](Circuit* circuit, const std::string& cnf_file) -> klay::NodePtr {
          return compile_from_cnf_using_sdd(circuit, cnf_file);
        },
        "circuit"_a, "cnf_file"_a,
        "Compile a CNF file by transforming it into an SDD and add the "
        "resulting nodes into an existing Circuit.");

  m.def("compile_from_sdd",
        [](Circuit* circuit, nb::object sdd_node_obj) -> klay::NodePtr {
          PyObject* capsule = nullptr;
          if (PyCapsule_CheckExact(sdd_node_obj.ptr())) {
            capsule = sdd_node_obj.ptr();
          } else {
            nb::object cap = sdd_node_obj.attr("_capsule");
            capsule = cap.ptr();
          }
          if (!PyCapsule_IsValid(capsule, "SddNode*")) {
            throw std::runtime_error(
                "Expected a PyCapsule with name 'SddNode*' "
                "(pass a pysdd.SddNode or its ._capsule)");
          }
          SddNode* root = static_cast<SddNode*>(
              PyCapsule_GetPointer(capsule, "SddNode*"));
          return compile_from_sdd(circuit, root);
        },
        "circuit"_a, "sdd_node"_a,
        "Transform a pysdd SddNode into an equivalent klay sub-circuit.");

  m.def("compile_from_cnf_using_d4v2",
        [](Circuit* circuit, const std::string& cnf_file) -> klay::NodePtr {
          return compile_from_cnf_using_d4v2(circuit, cnf_file);
        },
        "circuit"_a, "cnf_file"_a,
        "Compile a CNF file using D4V2 and add the resulting nodes into "
        "an existing Circuit.");

  m.def("compile_from_gates_formula_using_d4v2",
        [](Circuit* circuit, const GatedFormula* gf) -> klay::NodePtr {
          return compile_from_gates_using_d4v2(circuit, gf);
        },
        "circuit"_a, "formula"_a,
        "Compile a programmatically-constructed GatedFormula via d4v2 and "
        "add the resulting DNNF nodes into an existing Circuit.  The "
        "formula is resolved against the circuit's own name map, so "
        "re-using the same formula with a different circuit is fine.");

  m.def("compile_from_gates_file_using_d4v2",
        [](Circuit* circuit, const std::string& bc_file) -> klay::NodePtr {
          return compile_from_gates_using_d4v2(circuit, bc_file);
        },
        "circuit"_a, "bc_file"_a,
        "Compile a gate-formula file (BC-S1.2) via d4v2 and add the "
        "resulting DNNF nodes into an existing Circuit.");
}

}  // namespace kmpyl
