// Copyright (c) 2026 Ibrahim El Kaddouri
// Licensed under apachev2

#include "kompyle/kcircuit.h"

#include <string>

namespace kmpyl {

int Circuit::get_lit(const std::string& name) {
  auto it = names_.find(name);
  if (it == names_.end()) {
    it = names_.emplace(name, next_var_++).first;
  }
  return it->second;
}

}  // namespace kmpyl
