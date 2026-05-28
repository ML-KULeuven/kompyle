// Copyright (c) 2026 Ibrahim El Kaddouri
// Licensed under apachev2

#include "nanobind/nanobind.h"

#include "python/bindings.h"

NB_MODULE(pkompyle, m) {
  nanobind::module_::import_("klay");

  kmpyl::InitCircuitBindings(m);
  kmpyl::InitGatedFormulaBindings(m);
  kmpyl::InitCompileBindings(m);
  kmpyl::InitStatsBindings(m);
}
