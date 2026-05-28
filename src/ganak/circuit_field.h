// Copyright (c) 2026 Ibrahim El Kaddouri
// Licensed under apachev2

#pragma once

#include <boost/multiprecision/gmp.hpp>
#include <cryptominisat5/solvertypesmini.h>
#include <kompyle/kcircuit.h>
#include "field_stats.h"

#include <memory>
#include <chrono>
#include <string>
#include <unordered_set>

namespace kmpyl {

using mpz_int = boost::multiprecision::mpz_int;

class FCircuit final : public CMSat::Field {
 public:
  FCircuit(klay::NodePtr node, Circuit* circ, mpz_int val = 1)
      : node_(node), circ_(circ), val_(val) {}

  klay::Node* get_node() const {
    return node_.get();
  }

  mpz_int get_count() const {
    return val_;
  }

  Circuit* get_circuit() const {
    return circ_;
  }

  void add_lit(int ix) { lits_.insert(ix); }

  std::unique_ptr<Field> dup() const final;
  std::unique_ptr<Field> add(const Field& other) final;

  CMSat::Field& operator+=(const Field& other) final;
  CMSat::Field& operator*=(const Field& other) final;
  CMSat::Field& operator-=(const Field& other) final;
  CMSat::Field& operator/=(const Field& other) final;
  CMSat::Field& operator= (const Field& other) final;

  bool operator==(const Field& other) const final;

  bool is_zero() const final {
    return node_.get() && node_.get()->is_false();
  }

  bool is_one() const final {
    return node_.get() && node_.get()->is_true();
  }

  void set_zero() final;
  void set_one() final;

  std::ostream& display(std::ostream& os) const final;

  uint64_t bytes_used() const final { 
    return sizeof(FCircuit);
  }

  bool parse(const std::string&, const uint32_t) final {
    return false;
  }

 private:
  static const FCircuit& cast(const Field& f) {
    return static_cast<const FCircuit&>(f);
  }

  std::unique_ptr<Field> make(klay::NodePtr n, mpz_int val) const {
    return std::make_unique<FCircuit>(n, circ_, val);
  }

  klay::NodePtr node_;
  Circuit* circ_;
  mpz_int val_;
  std::unordered_set<int> lits_;
};

class FGenCircuit final : public CMSat::FieldGen {
 public:
  explicit FGenCircuit(Circuit* circ) : circ_(circ) {}

  Circuit* get_circuit() {
    return circ_;
  }

  std::unique_ptr<CMSat::Field> lit_field(int dimacs_lit) const;
  std::unique_ptr<CMSat::Field> zero() const final;
  std::unique_ptr<CMSat::Field> one() const final;
  std::unique_ptr<CMSat::FieldGen> dup() const final;

  bool larger_than(const CMSat::Field& a, const CMSat::Field& b) const final;

  bool weighted() const final {
    return true;
  }

 private:
  Circuit* circ_;
};

}  // namespace kmpyl
