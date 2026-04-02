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

NB_MODULE(pkompyle, m) {
  m.def("compile_from_cnf_using_ganak",
      [](Circuit* circuit, const std::string& cnf_file) -> NodePtr {
        return compile_from_cnf_using_ganak(circuit, cnf_file);
      },
      "circuit"_a, "cnf_file"_a,
      "Compile a CNF file using Ganak and add the resulting"
      "nodes into an existing Circuit."
  );
  m.def("compile_from_cnf_using_ganakarjun",
      [](Circuit* circuit, const std::string& cnf_file) -> NodePtr {
        return compile_from_cnf_using_ganakarjun(circuit, cnf_file);
      },
      "circuit"_a, "cnf_file"_a,
      "Compile a CNF file using Ganak + Arjun "
      "and add the resulting nodes into an existing Circuit."
  );
  m.def("compile_from_cnf_using_sdd",
      [](Circuit* circuit, const std::string& cnf_file) -> NodePtr {
        return compile_from_cnf_using_sdd(circuit, cnf_file);
      },
      "circuit"_a, "cnf_file"_a,
      "Compile a CNF file by transforming it into a sdd circuit and add the resulting"
      "nodes into an existing klay Circuit."
  );
  m.def("compile_from_sdd",
      [](Circuit* circuit, nb::object sdd_node_obj) -> NodePtr { 
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

        SddNode* root = static_cast<SddNode*>(PyCapsule_GetPointer(capsule, "SddNode*"));
        return compile_from_sdd(circuit, root);
      },
      "circuit"_a, "sdd_node"_a,
      "Transform a SddNode into an equivalent klay Circuit."
  );
}
