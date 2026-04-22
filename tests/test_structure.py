# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2

from util import assert_correct_structure

class TestCircuitStructure:

    def test_trivial_sat(self, pair_trivial_sat):
        assert_correct_structure(pair_trivial_sat)

    def test_trivial_unsat(self, pair_trivial_unsat):
        assert_correct_structure(pair_trivial_unsat)

    def test_tautology(self, pair_tautology):
        assert_correct_structure(pair_tautology)

    def test_xor(self, pair_xor):
        assert_correct_structure(pair_xor)

    def test_exactly_one(self, pair_exactly_one):
        assert_correct_structure(pair_exactly_one)

    def test_random_cnf(self, pair_random_structure):
        assert_correct_structure(pair_random_structure)

    def test_toy_file(self, pair_any_toy):
        assert_correct_structure(pair_any_toy)

    def test_unit_clause_only(self, pair_unit_clause_only):
        assert_correct_structure(pair_unit_clause_only)

    def test_unit_forced(self, pair_unit_forced):
        assert_correct_structure(pair_unit_forced)

    def test_unit_forced_unsat(self, pair_unit_forced_unsat):
        assert_correct_structure(pair_unit_forced_unsat)

    def test_unit_chain(self, pair_unit_chain):
        assert_correct_structure(pair_unit_chain)

    def test_unit_cascade_large(self, pair_unit_cascade_large):
        assert_correct_structure(pair_unit_cascade_large)

    # -----------------------------------------------------------------

    def test_gf_trivial_sat(self, gf_pair_trivial_sat):
        assert_correct_structure(gf_pair_trivial_sat)

    def test_gf_xor(self, gf_pair_xor):
        assert_correct_structure(gf_pair_xor)

    def test_gf_exactly_one(self, gf_pair_exactly_one):
        assert_correct_structure(gf_pair_exactly_one)

    def test_gf_random(self, gf_pair_random):
        assert_correct_structure(gf_pair_random)

    def test_gf_circ1(self, gf_pair_circ1):
        assert_correct_structure(gf_pair_circ1)

    def test_gf_noisy_or_2(self, gf_pair_noisy_or_2):
        assert_correct_structure(gf_pair_noisy_or_2)

    def test_gf_test(self, gf_pair_test):
        assert_correct_structure(gf_pair_test)

    def test_gf_verilog(self, gf_pair_verilog_jpsety_c17):
        assert_correct_structure(gf_pair_verilog_jpsety_c17)
