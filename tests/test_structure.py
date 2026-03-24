# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2

from util import assert_decomposable_and_smooth, compile_inline

class TestCircuitStructure:

    def test_trivial_sat(self, pair_trivial_sat):
        assert_decomposable_and_smooth(pair_trivial_sat.circuit,
                                       label=pair_trivial_sat.desc)

    def test_trivial_unsat(self, pair_trivial_unsat):
        assert_decomposable_and_smooth(pair_trivial_unsat.circuit,
                                       label=pair_trivial_unsat.desc)

    def test_tautology(self, pair_tautology):
        assert_decomposable_and_smooth(pair_tautology.circuit,
                                       label=pair_tautology.desc)

    def test_xor(self, pair_xor):
        assert_decomposable_and_smooth(pair_xor.circuit,
                                       label=pair_xor.desc)

    def test_exactly_one(self, pair_exactly_one):
        assert_decomposable_and_smooth(pair_exactly_one.circuit,
                                       label=pair_exactly_one.desc)

    def test_random_cnf(self, pair_random_structure):
        assert_decomposable_and_smooth(pair_random_structure.circuit,
                                       label=pair_random_structure.desc)

    def test_toy_file(self, pair_toy0):
        assert_decomposable_and_smooth(pair_toy0.circuit,
                                       label=pair_toy0.desc)

    def test_unit_clause_only(self):
        pair = compile_inline(1, [[1]], "unit-clause")
        assert_decomposable_and_smooth(pair.circuit,
                                       label=pair.desc)

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
        assert_decomposable_and_smooth(pair_unit_forced.circuit,
                                       label=pair_unit_forced.desc)

    def test_unit_forced_unsat(self, pair_unit_forced_unsat):
        assert_decomposable_and_smooth(pair_unit_forced_unsat.circuit,
                                       label=pair_unit_forced_unsat.desc)

    def test_unit_chain(self, pair_unit_chain):
        assert_decomposable_and_smooth(pair_unit_chain.circuit,
                                       label=pair_unit_chain.desc)

    def test_unit_cascade_large(self, pair_unit_cascade_large):
        assert_decomposable_and_smooth(pair_unit_cascade_large.circuit,
                                       label=pair_unit_cascade_large.desc)
