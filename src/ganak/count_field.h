#pragma once
#include <chrono>
#include <memory>
#include <string>

#include <boost/multiprecision/gmp.hpp>
#include <cryptominisat5/solvertypesmini.h>

#include "field_stats.h"

namespace kmpyl {

using mpz_int = boost::multiprecision::mpz_int;

class FCount final : public CMSat::Field {
 public:
  mpz_int val;
  explicit FCount(const mpz_int& v) : val(v) {}
  explicit FCount(long v) : val(v) {}

  std::unique_ptr<Field> dup() const final {
    ++g_gk_stats_count.n_dup;
    auto t0 = std::chrono::steady_clock::now();
    auto r = std::make_unique<FCount>(val);
    g_gk_stats_count.ns_dup += (std::chrono::steady_clock::now() - t0).count();
    return r;
  }

  Field& operator+=(const Field& other) final {
    ++g_gk_stats_count.n_add;
    auto t0 = std::chrono::steady_clock::now();
    val += static_cast<const FCount&>(other).val;
    g_gk_stats_count.ns_add += (std::chrono::steady_clock::now() - t0).count();
    return *this;
  }

  std::unique_ptr<Field> add(const Field& other) final {
    ++g_gk_stats_count.n_add;
    auto t0 = std::chrono::steady_clock::now();
    auto r = std::make_unique<FCount>(
        val + static_cast<const FCount&>(other).val);
    g_gk_stats_count.ns_add += (std::chrono::steady_clock::now() - t0).count();
    return r;
  }

  Field& operator*=(const Field& other) final {
    ++g_gk_stats_count.n_mul;
    auto t0 = std::chrono::steady_clock::now();
    val *= static_cast<const FCount&>(other).val;
    g_gk_stats_count.ns_mul += (std::chrono::steady_clock::now() - t0).count();
    return *this;
  }

  Field& operator=(const Field& o) final {
    val = static_cast<const FCount&>(o).val;
    return *this;
  }

  Field& operator-=(const Field& o) final {
    val -= static_cast<const FCount&>(o).val;
    return *this;
  }

  Field& operator/=(const Field& o) final {
    val /= static_cast<const FCount&>(o).val;
    return *this;
  }

  bool operator==(const Field& o) const final {
    return val == static_cast<const FCount&>(o).val;
  }

  bool is_zero() const final {
    return val == 0;
  }

  bool is_one()  const final {
    return val == 1;
  }

  void set_zero() final {
    val = 0;
  }

  void set_one() final {
    val = 1;
  }

  uint64_t bytes_used() const final {
    return sizeof(*this);
  }

  bool parse(const std::string&, uint32_t) final {
    return false;
  }

  std::ostream& display(std::ostream& os) const final {
    return os << val;
  }
};

class FGenCount final : public CMSat::FieldGen {
 public:
  explicit FGenCount(bool weighted = false) : weighted_(weighted) {}

  std::unique_ptr<CMSat::Field> zero() const final {
    ++g_gk_stats_count.n_zero;
    return std::make_unique<FCount>(0.0);
  }

  std::unique_ptr<CMSat::Field> one() const final {
    ++g_gk_stats_count.n_one;
    return std::make_unique<FCount>(1.0);
  }

  std::unique_ptr<CMSat::FieldGen> dup() const final {
    return std::make_unique<FGenCount>(weighted_);
  }

  bool larger_than(const CMSat::Field& a, const CMSat::Field& b) const final {
    return static_cast<const FCount&>(a).val >
           static_cast<const FCount&>(b).val;
  }

  bool weighted() const final {
    return weighted_;
  }

 private:
  bool weighted_;
};

} // namespace kmpyl
