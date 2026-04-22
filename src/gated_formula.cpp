// Copyright (c) 2026 Ibrahim El Kaddouri
// Licensed under apachev2

#include "kompyle/gated_formula.h"


// TODO(Ibrahim):
// first issue:
// lit_name_map should be given to ProblemManager
// such that when parsing bc file or from python
// variables names map to the same dimacs integer
// internally. this resolves the issue of mapping across different instances
//
// TODO(Ibrahim):
// second issue:
// having gate variables in klay:
// these need to be replaced with `True` nodes
// it would be best if that was done directly in KlayCircuitOperation!
// so, you need to know which variables in the list of gates
// aren't input variables.


namespace kmpyl {

const std::string&
GatedFormula::add_input(const std::string& name) {
  Gate g;
  g.kind = GateKind::IDENTITY;
  g.output = name;
  g.inputs = {name};
  gates_.push_back(std::move(g));
  return name;
}

const std::string&
GatedFormula::add_and(const std::string& output,
                      const std::vector<std::string>& inputs) {
  Gate g;
  g.kind = GateKind::AND;
  g.output = output;
  g.inputs = inputs;
  gates_.push_back(std::move(g));
  return output;
}

const std::string&
GatedFormula::add_or(const std::string& output,
                     const std::vector<std::string>& inputs) {
  Gate g;
  g.kind = GateKind::OR;
  g.output = output;
  g.inputs = inputs;
  gates_.push_back(std::move(g));
  return output;
}

const std::string&
GatedFormula::add_target(const std::string& token) {
  Gate g;
  g.kind = GateKind::TARGET;
  g.output = token;
  g.inputs = {};
  gates_.push_back(std::move(g));
  return token;
}

void GatedFormula::display(std::ostream& os) const {
  for (const auto& g : gates_) {
    switch (g.kind) {
      case GateKind::IDENTITY:
        os << "I " << g.output << "\n";
        break;
      case GateKind::AND:
      case GateKind::OR: {
        const char t = (g.kind == GateKind::AND) ? 'A' : 'O';
        os << "G " << g.output << " := " << t;
        for (const auto& in : g.inputs) os << " " << in;
        os << "\n";
        break;
      }
      case GateKind::TARGET:
        os << "T " << g.output << "\n";
        break;
    }
  }
}

}  // namespace kmpyl
