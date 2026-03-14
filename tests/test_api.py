import pytest
import kompyle as p
import klay as k

@pytest.fixture
def circuit():
    return k.Circuit()

def test_initial_nb_nodes(circuit):
    assert circuit.nb_nodes() == 0

def test_compile_from_ganak_into_existing_circuit(circuit):
    nptr = p.compile_from_ganak(circuit, "./assets/toy/toy0.cnf")
    circuit.set_root(nptr)
    assert circuit.nb_nodes() > 0

def test_compile_from_ganak_standalone(circuit):
    nptr1 = p.compile_from_ganak(circuit, "./assets/toy/toy0.cnf")
    nptr2 = p.compile_from_ganak("./assets/toy/toy0.cnf")
    circuit.set_root(nptr2)
    assert circuit.nb_nodes() > 0

def test_or_node(circuit):
    nptr1 = p.compile_from_ganak(circuit, "./assets/toy/toy0.cnf")
    nptr2 = p.compile_from_ganak("./assets/toy/toy0.cnf")
    nptr = circuit.or_node([nptr1, nptr2])
    circuit.set_root(nptr)
    assert circuit.nb_nodes() > 0

def test_get_indices(circuit):
    nptr1 = p.compile_from_ganak(circuit, "./assets/toy/toy0.cnf")
    nptr2 = p.compile_from_ganak("./assets/toy/toy0.cnf")
    nptr = circuit.or_node([nptr1, nptr2])
    circuit.set_root(nptr)
    indices = circuit._get_indices()
    assert indices is not None
