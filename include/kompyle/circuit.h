// Copyright (c) 2026 Ibrahim El Kaddouri
// Licensed under apachev2

#pragma once

#include <string>
#include <klay/circuit.h>
#include <md4/problem/circuit/LitNameMap.hpp>

namespace kmpyl {

class Circuit : public klay::Circuit {
 public:
  Circuit() = default;
  ~Circuit() override = default;

  Circuit(const Circuit&) = delete;
  Circuit& operator=(const Circuit&) = delete;
  Circuit(Circuit&&) = delete;
  Circuit& operator=(Circuit&&) = delete;

  int var_for_name(std::string& name) {
    return names_.get_lit(name).var();
  }

  int nb_vars() const {
    return static_cast<int>(names_.nextVar) - 1;
  }

  d4::LitNameMap& names() { return names_; }
  const d4::LitNameMap& names() const { return names_; }

 private:
  d4::LitNameMap names_;
};

}  // namespace kmpyl
