# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2

from util import assert_correct_structure, compile_inline

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

    # # def test_alarm(self, pair_alarm):
    # #     assert_decomposable_and_smooth(pair_alarm.circuit,
    # #                                    label=pair_alarm.desc)
    # #
    # # def test_child(self, pair_child):
    # #     assert_decomposable_and_smooth(pair_child.circuit,
    # #                                    label=pair_child.desc)
    # #
    # # def test_hailfinder(self, pair_hailfinder):
    # #     assert_decomposable_and_smooth(pair_hailfinder.circuit,
    # #                                    label=pair_hailfinder.desc)
    # #
    # # def test_munin(self, pair_munin):
    # #     assert_decomposable_and_smooth(pair_munin.circuit,
    # #                                    label=pair_munin.desc)
    # #
    # # def test_pathfinder(self, pair_pathfinder):
    # #     assert_decomposable_and_smooth(pair_pathfinder.circuit,
    # #                                    label=pair_pathfinder.desc)
    # #
    # # def test_pigs(self, pair_pigs):
    # #     assert_decomposable_and_smooth(pair_pigs.circuit,
    # #                                    label=pair_pigs.desc)
    #
    # # def test_count124(self, pair_count124):
    # #     assert_decomposable_and_smooth(pair_count124.circuit,
    # #                                    label=pair_count124.desc)
    # #
    # # def test_count153(self, pair_count153):
    # #     assert_decomposable_and_smooth(pair_count153.circuit,
    # #                                    label=pair_count153.desc)

    def test_unit_forced(self, pair_unit_forced):
        assert_correct_structure(pair_unit_forced)

    def test_unit_forced_unsat(self, pair_unit_forced_unsat):
        assert_correct_structure(pair_unit_forced_unsat)

    def test_unit_chain(self, pair_unit_chain):
        assert_correct_structure(pair_unit_chain)

    def test_unit_cascade_large(self, pair_unit_cascade_large):
        assert_correct_structure(pair_unit_cascade_large)
