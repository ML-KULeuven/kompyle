# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2

import kompyle as p

from util import write_cnf
from pysdd.sdd   import SddManager

from util import ( assert_exhaustive_equivalence,
    compile_gated,
)

class TestAPI:
    def test_initial_nb_nodes(self):
        circuit = p.Circuit()
        assert circuit.nb_nodes() == 0

    def test_compile_ganak(self):
        circuit = p.Circuit()
        path = "./assets/toy/toy2.cnf"

        gopt = p.GanakOptions()
        gopt.do_restart = True

        aopt = p.ArjunOptions()
        aopt.do_arjun = False

        nptr = p.compile_from_cnf_using_ganak(circuit, path,
                                              # ganak_options=gopt,
                                              arjun_options=aopt)

        circuit.set_root(nptr)
        assert circuit.nb_nodes() > 0
        assert circuit.nb_root_nodes() == 1

    def test_compile_d4(self):
        circuit = p.Circuit()
        path = "./assets/toy/toy2.cnf"

        nptr = p.compile_from_cnf_using_d4v2(circuit, path)

        circuit.set_root(nptr)
        assert circuit.nb_nodes() > 0
        assert circuit.nb_root_nodes() == 1

    def test_count_ganak(self):
        circuit = p.Circuit()
        path = "./assets/toy/toy2.cnf"

        gopt = p.GanakOptions()
        gopt.do_restart = True

        aopt = p.ArjunOptions()
        aopt.do_arjun = True

        count = p.count_from_cnf_using_ganak(path,
                                             ganak_options=gopt,
                                             arjun_options=aopt)

    def test_count_d4(self):
        circuit = p.Circuit()
        path = "./assets/toy/toy2.cnf"

        nptr = p.compile_from_cnf_using_d4v2(circuit, path)

        circuit.set_root(nptr)
        assert circuit.nb_nodes() > 0
        assert circuit.nb_root_nodes() == 1

    def test_compile_from_ganak_xor(self):
        circuit = p.Circuit()
        path = write_cnf(3, [[1, 2], [-1, -2]])
        aopt = p.ArjunOptions()
        aopt.do_arjun = False
        nptr = p.compile_from_cnf_using_ganak(circuit, path, arjun_options=aopt)
        circuit.set_root(nptr)
        assert circuit.nb_nodes() > 0
        assert circuit.nb_root_nodes() == 1

    def test_count_from_ganak_xor(self):
        circuit = p.Circuit()
        path = write_cnf(3, [[1, 2], [-1, -2]])
        aopt = p.ArjunOptions()
        aopt.do_arjun = False
        count = p.count_from_cnf_using_ganak(path, arjun_options=aopt)

    def test_compile_from_cnf_using_sdd(self):
        circuit = p.Circuit()
        path = write_cnf(3, [[1, 2], [-1, -2]])
        nptr = p.compile_from_cnf_using_sdd(circuit, path)
        circuit.set_root(nptr)
        assert circuit.nb_nodes() > 0
        assert circuit.nb_root_nodes() == 1

    def test_compile_from_sdd(self):
        circuit = p.Circuit()
        path = write_cnf(3, [[1, 2], [-1, -2]])
        mgr, sdd_node = SddManager.from_cnf_file(path.encode(), vtree_type=b"balanced")
        nptr = p.compile_from_sdd(circuit, sdd_node)
        circuit.set_root(nptr)
        assert circuit.nb_nodes() > 0
        assert circuit.nb_root_nodes() == 1

    # TODO(Ibrahim):
    # set d4v2 verbosity off

    def test_compile_from_cnf_using_d4v2(self):
        circuit = p.Circuit()
        path = write_cnf(3, [[1, 2], [-1, -2]])
        nptr = p.compile_from_cnf_using_d4v2(circuit, path)
        circuit.set_root(nptr)
        assert circuit.nb_nodes() > 0 # and circuit.nb_nodes() == 170
        assert circuit.nb_root_nodes() == 1

    def test_compile_from_cnf_using_d4v2_pair_trivial(self):
        circuit = p.Circuit()
        path = write_cnf(2, [[1, 2]])
        nptr = p.compile_from_cnf_using_d4v2(circuit, path)
        circuit.set_root(nptr)
        assert circuit.nb_nodes() > 0
        assert circuit.nb_root_nodes() == 1

        nptr = p.compile_from_cnf_using_d4v2(circuit, path)
        circuit.set_root(nptr)
        assert circuit.nb_nodes() > 0
        assert circuit.nb_root_nodes() == 2

    def test_compile_from_cnf_using_d4v2_pair_xor(self):
        circuit = p.Circuit()
        path = write_cnf(3, [[1, 2], [-1, -2]])
        nptr = p.compile_from_cnf_using_d4v2(circuit, path)
        circuit.set_root(nptr)
        assert circuit.nb_nodes() > 0
        assert circuit.nb_root_nodes() == 1

        nptr = p.compile_from_cnf_using_d4v2(circuit, path)
        circuit.set_root(nptr)
        assert circuit.nb_nodes() > 0
        assert circuit.nb_root_nodes() == 2

    def test_compile_from_gates_using_d4v2(self):
        gf = p.GatedFormula()
        gf.add_input('x1')
        gf.add_input('x2')
        gf.add_and('g3', ['x1', 'x2'])
        gf.add_target('g3')

        circuit = p.Circuit()
        root = p.compile_from_gates_formula_using_d4v2(circuit, gf)
        circuit.set_root(root)
        assert circuit.nb_nodes() > 0

    def test_trivial_sat(self):
        nice = compile_gated(2, [[1, 2]], "trivial-sat")
        assert_exhaustive_equivalence(nice)

    def test_compile_from_ganak_toy0(self):
        circuit = p.Circuit()
        nptr = p.compile_from_cnf_using_ganak(circuit, "./assets/toy/toy0.cnf")
        circuit.set_root(nptr)
        assert circuit.nb_nodes() > 0
        assert circuit.nb_root_nodes() == 1

    def test_compile_from_ganak_toy1(self):
        circuit = p.Circuit()
        nptr = p.compile_from_cnf_using_ganak(circuit, "./assets/toy/toy1.cnf")
        circuit.set_root(nptr)
        assert circuit.nb_nodes() > 0
        assert circuit.nb_root_nodes() == 1

    # NOTE(Ibrahim):
    # you have to set_root before recalling
    # compile_from_ganak due to arjun!
    def test_or_node(self):
        circuit = p.Circuit()

        nptr1 = p.compile_from_cnf_using_ganak(circuit, "./assets/toy/toy0.cnf")
        circuit.set_root(nptr1)
        nbn1 = circuit.nb_nodes()
        nbrn1 = circuit.nb_root_nodes()

        nptr2 = p.compile_from_cnf_using_ganak(circuit, "./assets/toy/toy1.cnf")
        circuit.set_root(nptr2)
        nbn2 = circuit.nb_nodes()
        nbrn2 = circuit.nb_root_nodes()

        nptr3 = circuit.or_node([nptr1, nptr2])
        circuit.set_root(nptr3)
        nbn3 = circuit.nb_nodes()
        nbrn3 = circuit.nb_root_nodes()

        # NOTE(Ibrahim):
        # klay/circuit reuses nodes based on hash value!
        # doesn't construct a 2nd layer circuit on top!

        assert circuit.nb_nodes() > 0
        assert nbn1 != nbn2
        assert nbn2 != nbn3
        assert nbrn1 + nbrn2 + nbrn3 == 6

    def test_remove_unused_nodes(self):
        circuit = p.Circuit()

        nptr1 = p.compile_from_cnf_using_ganak(circuit, "./assets/toy/toy0.cnf")
        nptr2 = p.compile_from_cnf_using_ganak(circuit, "./assets/toy/toy1.cnf")
        circuit.or_node([nptr1, nptr2])

        circuit.remove_unused_nodes() # doesn't remove layer 0
        assert circuit.nb_nodes() == (6 * 2) + 2

    def test_set_root(self):
        circuit = p.Circuit()

        nptr1 = p.compile_from_cnf_using_ganak(circuit, "./assets/toy/toy0.cnf")
        nptr2 = p.compile_from_cnf_using_ganak(circuit, "./assets/toy/toy1.cnf")
        nptr3 = circuit.or_node([nptr1, nptr2])
        circuit.set_root(nptr3)

        circuit.remove_unused_nodes() # doesn't remove layer 0
        assert circuit.nb_nodes() > (6 * 2) + 2

    def test_get_indices(self):
        circuit = p.Circuit()
        nptr1 = p.compile_from_cnf_using_ganak(circuit, "./assets/toy/toy0.cnf")
        circuit.set_root(nptr1)
        circuit.remove_unused_nodes()
        indices = circuit._get_indices()
        assert indices is not None
        assert len(indices) == 2
