// Copyright (c) 2026 Ibrahim El Kaddouri
// Licensed under apachev2

#include "kompyle/gated_formula.h"

#include <ostream>
#include <string>
#include <utility>
#include <vector>

namespace kmpyl {

const std::string& GatedFormula::add_input(const std::string& name) {
  Gate g;
  g.kind = GateKind::kIdentity;
  g.output = name;
  g.inputs = {name};
  gates_.push_back(std::move(g));
  return name;
}

const std::string& GatedFormula::add_and(
    const std::string& output,
    const std::vector<std::string>& inputs) {
  Gate g;
  g.kind = GateKind::kAnd;
  g.output = output;
  g.inputs = inputs;
  gates_.push_back(std::move(g));
  return output;
}

const std::string& GatedFormula::add_or(
    const std::string& output,
    const std::vector<std::string>& inputs) {
  Gate g;
  g.kind = GateKind::kOr;
  g.output = output;
  g.inputs = inputs;
  gates_.push_back(std::move(g));
  return output;
}

const std::string& GatedFormula::add_target(const std::string& token) {
  Gate g;
  g.kind = GateKind::kTarget;
  g.output = token;
  g.inputs = {};
  gates_.push_back(std::move(g));
  return token;
}

void GatedFormula::display(std::ostream& os) const {
  for (const auto& g : gates_) {
    switch (g.kind) {
      case GateKind::kIdentity:
        os << "I " << g.output << "\n";
        break;
      case GateKind::kAnd:
      case GateKind::kOr: {
        const char t = (g.kind == GateKind::kAnd) ? 'A' : 'O';
        os << "G " << g.output << " := " << t;
        for (const auto& in : g.inputs) os << " " << in;
        os << "\n";
        break;
      }
      case GateKind::kTarget:
        os << "T " << g.output << "\n";
        break;
    }
  }
}

}  // namespace kmpyl
