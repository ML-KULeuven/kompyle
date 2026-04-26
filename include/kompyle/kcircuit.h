// Copyright (c) 2026 Ibrahim El Kaddouri
// Licensed under apachev2

#ifndef INCLUDE_KOMPYLE_KCIRCUIT_H_
#define INCLUDE_KOMPYLE_KCIRCUIT_H_

#include <string>
#include <unordered_map>

#include "klay/circuit.h"

namespace kmpyl {

// A klay::Circuit that also owns a `string -> int` variable-name map.
//
// Knowledge-compilation pipelines turn formulas (CNFs, gate descriptions)
// into klay node graphs. When several gated formulas are compiled into the same
// circuit, they need to agree on which integer represents which named
// variable, otherwise downstream analyses produce nonsense.
// Every `get_lit(name)` call within a single instance returns the same
// DIMACS index for the same `name`.
//
// Indices are 1-based DIMACS-style: variable IDs start at 1 and grow
// monotonically as new names are seen. There is no zero variable.
//
// Instances are *not* thread-safe. Different `Circuit` instances may
// be used concurrently, but a single instance must not be accessed from
// more than one thread at a time.
//
// Example:
//
//     kmpyl::Circuit c;
//     auto* root = kmpyl::CompileFromCnfUsingD4v2(&c, "f.bc");
//     // `root` is owned by `c`, do not use it after `c` is destroyed.
class Circuit : public klay::Circuit {
 public:
  Circuit() = default;
  ~Circuit() override = default;

  // Not copyable or movable: a Circuit owns klay::Node objects whose raw
  // pointers are handed out elsewhere, relocating would invalidate them.
  Circuit(const Circuit&) = delete;
  Circuit& operator=(const Circuit&) = delete;
  Circuit(Circuit&&) = delete;
  Circuit& operator=(Circuit&&) = delete;

  // Returns the DIMACS variable index associated with `name`. Allocates a
  // fresh index on first use.

  // Returns the DIMACS variable index associated with `name`. The first
  // call for a given `name` allocates a fresh index, subsequent calls
  // return the same index.
  int get_lit(const std::string& name);

  // Number of distinct variable names registered so far.
  int nb_vars() const { return next_var_ - 1; }

 private:
  int next_var_ = 1;
  std::unordered_map<std::string, int> names_;
};

}  // namespace kmpyl

#endif  // INCLUDE_KOMPYLE_KCIRCUIT_H_
