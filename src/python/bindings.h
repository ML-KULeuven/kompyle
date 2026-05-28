// Copyright (c) 2026 Ibrahim El Kaddouri
// Licensed under apachev2

#ifndef SRC_PYTHON_BINDINGS_H_
#define SRC_PYTHON_BINDINGS_H_

#include "nanobind/nanobind.h"
#include "nanobind/stl/vector.h"  // IWYU pragma: keep
#include "nanobind/stl/string.h"  // IWYU pragma: keep

namespace kmpyl {

// Register nanobind bindings for each logical chunk of the module. Each
// function is defined in its own translation unit, `module.cc` stitches
// them together inside a single NB_MODULE.
void InitCircuitBindings(nanobind::module_& m);
void InitGatedFormulaBindings(nanobind::module_& m);
void InitCompileBindings(nanobind::module_& m);
void InitStatsBindings(nanobind::module_& m);

}  // namespace kmpyl

#endif  // SRC_PYTHON_BINDINGS_H_
