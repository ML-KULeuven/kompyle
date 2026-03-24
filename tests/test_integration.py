# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2

from util import assert_exhaustive_equivalence

class TestExhaustiveEquivalence:
    def test_trivial_sat(self, pair_trivial_sat):
        assert_exhaustive_equivalence(pair_trivial_sat)

    def test_trivial_unsat(self, pair_trivial_unsat):
        assert_exhaustive_equivalence(pair_trivial_unsat)

    def test_tautology(self, pair_tautology):
        assert_exhaustive_equivalence(pair_tautology)

    def test_xor(self, pair_xor):
        assert_exhaustive_equivalence(pair_xor)

    def test_exactly_one(self, pair_exactly_one):
        assert_exhaustive_equivalence(pair_exactly_one)

    def test_random_cnf(self, pair_random):
        assert_exhaustive_equivalence(pair_random)

    def test_toy_file(self, pair_toy0):
        assert_exhaustive_equivalence(pair_toy0)

    def test_unit_forced(self, pair_unit_forced):
        assert_exhaustive_equivalence(pair_unit_forced)

    def test_unit_forced_unsat(self, pair_unit_forced_unsat):
        assert_exhaustive_equivalence(pair_unit_forced_unsat)

    def test_unit_chain(self, pair_unit_chain):
        assert_exhaustive_equivalence(pair_unit_chain)
