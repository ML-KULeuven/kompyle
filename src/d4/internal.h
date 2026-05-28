// Copyright (c) 2026 Ibrahim El Kaddouri
// Licensed under apachev2
//
// Internal helpers shared between d4 compile and d4 count.

#ifndef SRC_D4_INTERNAL_H_
#define SRC_D4_INTERNAL_H_

#include <fcntl.h>
#include <unistd.h>

#include <cstdio>
#include <string>

#include "md4/configurations/ConfigurationCache.hpp"
#include "md4/configurations/ConfigurationBranchingHeuristic.hpp"
#include "md4/configurations/ConfigurationPreproc.hpp"
#include "md4/configurations/ConfigurationSolver.hpp"
#include "md4/problem/ProblemManager.hpp"

#include "kompyle/options.h"

namespace kmpyl {
namespace d4_internal {

d4::SolverName MapSolverName(D4Solver s);

d4::PreprocMethod MapPreprocMethod(D4PreprocMethod m);

d4::ConfigurationPeproc MakePreprocConfig(
    const D4Options& opts,
    d4::ProblemInputType input_type);

d4::ConfigurationCache MakeCacheConfig(const D4Options& opts);

d4::ConfigurationBranchingHeuristic MakeBranchingConfig(const D4Options& opts);

// d4v2 is chatty on stdout. We redirect fd 1 to /dev/null for the lifetime
// of the object so the count/compile entry points don't pollute Python stdout.
class StdoutSilencer {
 public:
  StdoutSilencer();
  ~StdoutSilencer();
  StdoutSilencer(const StdoutSilencer&) = delete;
  StdoutSilencer& operator=(const StdoutSilencer&) = delete;
 private:
  int saved_;
  int devnull_;
};

}  // namespace d4_internal
}  // namespace kmpyl

#endif  // SRC_D4_INTERNAL_H_
