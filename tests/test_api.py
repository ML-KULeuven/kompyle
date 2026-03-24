# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2

import kompyle as p
import klay as k

class TestAPI:
    def test_initial_nb_nodes(self):
        circuit = k.Circuit()
        assert circuit.nb_nodes() == 0

    def test_compile_from_ganak_toy0(self):
        circuit = k.Circuit()
        nptr = p.compile_from_ganak(circuit, "./assets/toy/toy0.cnf")
        circuit.set_root(nptr)
        assert circuit.nb_nodes() > 0 # and circuit.nb_nodes() == 170
        assert circuit.nb_root_nodes() == 1

    def test_compile_from_ganak_toy1(self):
        circuit = k.Circuit()
        nptr = p.compile_from_ganak(circuit, "./assets/toy/toy1.cnf")
        circuit.set_root(nptr)
        assert circuit.nb_nodes() > 0 # and circuit.nb_nodes() == 94
        assert circuit.nb_root_nodes() == 1

    # NOTE(Ibrahim):
    # you have to set_root before recalling
    # compile_from_ganak due to arjun!
    def test_or_node(self):
        circuit = k.Circuit()

        nptr1 = p.compile_from_ganak(circuit, "./assets/toy/toy0.cnf")
        circuit.set_root(nptr1)
        nbn1 = circuit.nb_nodes()
        nbrn1 = circuit.nb_root_nodes()

        nptr2 = p.compile_from_ganak(circuit, "./assets/toy/toy1.cnf")
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
        circuit = k.Circuit()

        nptr1 = p.compile_from_ganak(circuit, "./assets/toy/toy0.cnf")
        nptr2 = p.compile_from_ganak(circuit, "./assets/toy/toy1.cnf")
        circuit.or_node([nptr1, nptr2])

        circuit.remove_unused_nodes() # doesn't remove layer 0
        assert circuit.nb_nodes() == (6 * 2) + 2

    def test_set_root(self):
        circuit = k.Circuit()

        nptr1 = p.compile_from_ganak(circuit, "./assets/toy/toy0.cnf")
        nptr2 = p.compile_from_ganak(circuit, "./assets/toy/toy1.cnf")
        nptr3 = circuit.or_node([nptr1, nptr2])
        circuit.set_root(nptr3)

        circuit.remove_unused_nodes() # doesn't remove layer 0
        assert circuit.nb_nodes() > (6 * 2) + 2

    def test_get_indices(self):
        circuit = k.Circuit()
        nptr1 = p.compile_from_ganak(circuit, "./assets/toy/toy0.cnf")
        circuit.set_root(nptr1)
        circuit.remove_unused_nodes()
        indices = circuit._get_indices()
        assert indices is not None
        assert len(indices) == 2
