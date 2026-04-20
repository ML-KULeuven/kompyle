// Copyright (c) 2026 Ibrahim El Kaddouri
// Licensed under apachev2
#pragma once

#include <iosfwd>
#include <string>
#include <vector>
#include <utility>
#include <ostream>

namespace kmpyl {

class GatedFormula {
 public:
  enum class GateKind { AND, OR, IDENTITY, TARGET };

  struct Gate {
    GateKind kind;
    std::string output;
    std::vector<std::string> inputs;
  };

  GatedFormula() = default;

  const std::string&
  add_and(const std::string& output, const std::vector<std::string>& inputs);

  const std::string&
  add_or(const std::string& output, const std::vector<std::string>& inputs);

  const std::string&
  add_input(const std::string& name);

  const std::string&
  add_target(const std::string& token);

  const std::vector<Gate>&
  gates() const { return gates_; }

  // const std::vector<std::string>&
  // targets() const { return targets_; }

  void display(std::ostream& os) const;

 private:
  std::vector<Gate> gates_;
  // std::vector<std::string> targets_;
};

}  // namespace kmpyl
