// Copyright (c) 2026 Ibrahim El Kaddouri
// Licensed under apachev2

#ifndef SRC_D4_MPZ_COUNTING_OPERATION_H_
#define SRC_D4_MPZ_COUNTING_OPERATION_H_

#include <cstdint>
#include <vector>

#include <boost/multiprecision/gmp.hpp>

#include "md4/methods/OperationManager.hpp"

#include "d4/d4_stats.h"

namespace kmpyl {

class CountingOperation
    : public d4::Operation<boost::multiprecision::mpz_int,
                           boost::multiprecision::mpz_int> {
 public:
  using mpz_int = boost::multiprecision::mpz_int;

  CountingOperation() = default;
  ~CountingOperation() override = default;

  mpz_int createTop() override {
    ++g_d4_stats_count.n_top;
    D4ScopedTimer t(g_d4_stats_count.ns_top);
    return mpz_int(1);
  }

  mpz_int createBottom() override {
    ++g_d4_stats_count.n_bottom;
    D4ScopedTimer t(g_d4_stats_count.ns_bottom);
    return mpz_int(0);
  }

  mpz_int manageBottom() override {
    return createBottom();
  }

  mpz_int manageTop(std::vector<d4::Var>& freeVars) override {
    ++g_d4_stats_count.n_top;
    D4ScopedTimer t(g_d4_stats_count.ns_top);
    return Pow2(freeVars.size());
  }

  mpz_int manageBranch(d4::DataBranch<mpz_int>& b) override {
    ++g_d4_stats_count.n_branch;
    D4ScopedTimer t(g_d4_stats_count.ns_branch);
    return WrapBranch(b);
  }

  mpz_int manageDeterministOr(d4::DataBranch<mpz_int>* elts,
                              unsigned size) override {
    ++g_d4_stats_count.n_add;
    D4ScopedTimer t(g_d4_stats_count.ns_add);

    mpz_int s = 0;
    for (unsigned i = 0; i < size; ++i) {
      s += WrapBranch(elts[i]);
    }
    return s;
  }

  mpz_int manageDecomposableAnd(mpz_int* elts, unsigned size) override {
    ++g_d4_stats_count.n_mul;
    D4ScopedTimer t(g_d4_stats_count.ns_mul);

    mpz_int p = 1;
    for (unsigned i = 0; i < size; ++i) p *= elts[i];
    return p;
  }

  mpz_int count(mpz_int& v) override {
    return v;
  }

  mpz_int count(mpz_int& v, std::vector<d4::Lit>&) override {
    return v;
  }

 private:
  static mpz_int WrapBranch(d4::DataBranch<mpz_int>& b) {
    return b.d * Pow2(b.freeVars.size());
  }

  static mpz_int Pow2(std::size_t n) {
    return mpz_int(1) << n;
  }
};

}  // namespace kmpyl

#endif  // SRC_D4_MPZ_COUNTING_OPERATION_H_
