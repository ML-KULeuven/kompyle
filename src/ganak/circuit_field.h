// Copyright (c) 2026 Ibrahim El Kaddouri
// Licensed under apachev2

#ifndef SRC_GANAK_CIRCUIT_FIELD_H_
#define SRC_GANAK_CIRCUIT_FIELD_H_

#include <memory>
#include <string>
#include <unordered_map>
#include <vector>

#include "klay/node.h"
#include "cryptominisat5/solvertypesmini.h"

#include "kompyle/kcircuit.h"

namespace kmpyl {

// A CMSat::Field whose "value" is a list of klay circuit factors. Each
// arithmetic op on FCircuit corresponds to a structural op on the
// underlying circuit.
class FCircuit final : public CMSat::Field {
 public:
  FCircuit(klay::Node* node, Circuit* circuit, double count = 1.0);

  klay::Node* get_node() const { return Materialise(); }
  Circuit* get_circuit() const { return circuit_; }
  double get_count() const { return count_; }

  std::unique_ptr<CMSat::Field> dup() const final;
  std::unique_ptr<CMSat::Field> add(const CMSat::Field& other) final;

  CMSat::Field& operator+=(const CMSat::Field& other) final;
  CMSat::Field& operator*=(const CMSat::Field& other) final;
  CMSat::Field& operator-=(const CMSat::Field& other) final;
  CMSat::Field& operator/=(const CMSat::Field& other) final;
  CMSat::Field& operator=(const CMSat::Field& other) final;

  bool operator==(const CMSat::Field& other) const final;

  bool is_zero() const final { return is_zero_; }
  bool is_one() const final;

  std::ostream& display(std::ostream& os) const final;

  void set_zero() final;
  void set_one() final;

  uint64_t bytes_used() const final { return sizeof(FCircuit); }
  bool parse(const std::string&, const uint32_t) final { return false; }

 private:
  static const FCircuit& Cast(const CMSat::Field& f) {
    return static_cast<const FCircuit&>(f);
  }

  klay::Node* Materialise() const;
  void PushFactor(klay::Node* n);

  Circuit* circuit_;

  // TODO(Ibrahim): double is not precise enough for large counts.
  double count_;
  bool is_zero_ = false;
  std::vector<klay::Node*> factors_;
  std::unordered_map<int, std::size_t> lit_to_factor_;
};

// CMSat::FieldGen that produces FCircuit instances bound to a given Circuit.
class FGenCircuit final : public CMSat::FieldGen {
 public:
  explicit FGenCircuit(Circuit* circuit) : circuit_(circuit) {}

  Circuit* get_circuit() { return circuit_; }

  std::unique_ptr<CMSat::Field> lit_field(int dimacs_lit) const;
  std::unique_ptr<CMSat::Field> zero() const final;
  std::unique_ptr<CMSat::Field> one() const final;
  std::unique_ptr<CMSat::FieldGen> dup() const final;

  bool larger_than(const CMSat::Field& a,
                   const CMSat::Field& b) const final;

  bool exact() const { return false; }
  bool weighted() const final { return true; }

 private:
  Circuit* circuit_;
};

}  // namespace kmpyl

#endif  // SRC_GANAK_CIRCUIT_FIELD_H_
