#pragma once

#include <boost/multiprecision/gmp.hpp>
#include <cryptominisat5/solvertypesmini.h>
#include <kompyle/kcircuit.h>
#include "field_stats.h"

#include <memory>
#include <chrono>
#include <string>

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

  std::unique_ptr<Field> dup() const final {
    ++g_gk_stats_circuit.n_dup;
    auto t0 = std::chrono::steady_clock::now();
    auto r = std::make_unique<FCircuit>(node_, circ_);
    r->val_ = val_;
    g_gk_stats_circuit.ns_dup += (std::chrono::steady_clock::now() - t0).count();
    return r;
  }

  std::unique_ptr<Field> add(const Field& other) final {
    ++g_gk_stats_circuit.n_add;
    auto t0 = std::chrono::steady_clock::now();
    const auto& o = cast(other);
    auto r = make(circ_->or_node({ node_, o.node_ }), val_ + o.val_);
    g_gk_stats_circuit.ns_add += (std::chrono::steady_clock::now() - t0).count();
    return r;
  }

  Field& operator+=(const Field& other) final {
    ++g_gk_stats_circuit.n_add;
    auto t0 = std::chrono::steady_clock::now();
    const auto& o = cast(other);
    node_ = circ_->or_node({ node_, o.node_ });
    val_ += o.val_;
    g_gk_stats_circuit.ns_add += (std::chrono::steady_clock::now() - t0).count();
    return *this;
  }

  Field& operator*=(const Field& other) final {
    ++g_gk_stats_circuit.n_mul;
    auto t0 = std::chrono::steady_clock::now();
    const auto& o = cast(other);
    node_ = circ_->and_node({ node_, o.node_ });
    val_ *= o.val_;
    g_gk_stats_circuit.ns_mul += (std::chrono::steady_clock::now() - t0).count();
    return *this;
  }

  Field& operator-=(const Field& other) final {
    const auto& o = cast(other);
    val_ -= o.val_;
    return *this;
  }

  Field& operator/=(const Field& other) final {
    const auto& o = cast(other);
    val_ /= o.val_;
    return *this;
  }

  Field& operator=(const Field& other) final {
    const auto& o = cast(other);
    node_ = o.node_;
    circ_ = o.circ_;
    val_  = o.val_;
    return *this;
  }

  bool operator==(const Field& other) const final {
    const auto& o = cast(other);
    klay::Node* tn = node_.get();
    klay::Node* on = o.get_node();
    // return tn->hash   == on->hash   &&
    //        tn->layer  == on->layer  &&
    //        tn->ix     == on->ix;
    return node_ == cast(other).node_;
  }

  bool is_zero() const final {
    return node_.get() && node_.get()->is_false();
  }

  bool is_one()  const final {
    return node_.get() && node_.get()->is_true();
  }

  void set_zero() final {
    val_ = 0;
    node_ = circ_->false_node();
  }

  void set_one()  final {
    val_ = 1;
    node_ = circ_->true_node();
  }

  std::ostream& display(std::ostream& os) const final {
    if (node_.get()) os << node_.get()->get_label();
    else             os << "null";
    return os;
  }

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
};

class FGenCircuit final : public CMSat::FieldGen {
 public:
  explicit FGenCircuit(Circuit* circ) : circ_(circ) {}

  Circuit* get_circuit() {
    return circ_;
  }

  std::unique_ptr<CMSat::Field> lit_field(int dimacs_lit) const {
    ++g_gk_stats_circuit.n_lit_field;
    auto t0 = std::chrono::steady_clock::now();
    auto a = std::make_unique<FCircuit>(circ_->literal_node(dimacs_lit), circ_, 1);
    g_gk_stats_circuit.ns_lit_field += (std::chrono::steady_clock::now() - t0).count();
    return a;
  }

  std::unique_ptr<CMSat::Field> zero() const final {
    ++g_gk_stats_circuit.n_zero;
    auto t0 = std::chrono::steady_clock::now();
    auto a = std::make_unique<FCircuit>(circ_->false_node(), circ_, 0);
    g_gk_stats_circuit.ns_zero += (std::chrono::steady_clock::now() - t0).count();
    return a;
  }

  std::unique_ptr<CMSat::Field> one() const final {
    ++g_gk_stats_circuit.n_one;
    auto t0 = std::chrono::steady_clock::now();
    auto a = std::make_unique<FCircuit>(circ_->true_node(), circ_, 1);
    g_gk_stats_circuit.ns_one += (std::chrono::steady_clock::now() - t0).count();
    return a;
  }

  std::unique_ptr<CMSat::FieldGen> dup() const final {
    ++g_gk_stats_circuit.n_gen_dup;
    auto t0 = std::chrono::steady_clock::now();
    auto a = std::make_unique<FGenCircuit>(circ_);
    g_gk_stats_circuit.ns_gen_dup += (std::chrono::steady_clock::now() - t0).count();
    return a;
  }

  bool larger_than(const CMSat::Field& a, const CMSat::Field& b) const final {
    return static_cast<const FCircuit&>(a).get_count() >
           static_cast<const FCircuit&>(b).get_count() ;
  }

  bool weighted() const final {
    return true;
  }

 private:
  Circuit* circ_;
};

}  // namespace kmpyl
