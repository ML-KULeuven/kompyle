// Copyright (c) 2026 Ibrahim El Kaddouri
// Licensed under apachev2

#ifndef INCLUDE_KOMPYLE_GATED_FORMULA_H_
#define INCLUDE_KOMPYLE_GATED_FORMULA_H_

#include <iosfwd>
#include <string>
#include <vector>

namespace kmpyl {

// Programmatic builder for BC-S1.2-style gate formulas.
//
// A `GatedFormula` is a pure value: it records inputs, gates, and target
// literals by *string name*. It holds no reference to any circuit and no
// integer indices, which means the same instance can be compiled into
// any number of independent `Circuit`s and each compilation will resolve
// names against that circuit's own name map.
//
// This class is *not* thread-safe.
//
// Example:
//
//     kmpyl::GatedFormula gf;
//     gf.add_input("a");
//     gf.add_input("b");
//     gf.add_and("g1", {"a", "-b"});
//     gf.add_target("g1");
class GatedFormula {
 public:
  enum class GateKind { kAnd, kOr, kIdentity, kTarget };

  struct Gate {
    GateKind kind;
    std::string output;
    std::vector<std::string> inputs;
  };

  GatedFormula() = default;

  // Append a gate: output := AND(inputs). Inputs may start with '-' for
  // negation. Returns a reference to the stored output name.
  const std::string& add_and(const std::string& output,
                             const std::vector<std::string>& inputs);

  // Append a gate `output := OR(inputs)`. Returns a reference to the
  // stored copy of `output` for chaining.
  const std::string& add_or(const std::string& output,
                            const std::vector<std::string>& inputs);

  // Declare an input variable (BC-S1.2 'I' line).
  const std::string& add_input(const std::string& name);

  // Mark a literal as a target (BC-S1.2 'T' line).
  // `token` may start with '-' for negation.
  const std::string& add_target(const std::string& token);

  // All gates in declaration order.
  const std::vector<Gate>& gates() const { return gates_; }

  // Pretty-print the formula in BC-S1.2 syntax for debugging.
  void display(std::ostream& os) const;

 private:
  std::vector<Gate> gates_;
};

}  // namespace kmpyl

#endif  // INCLUDE_KOMPYLE_GATED_FORMULA_H_
