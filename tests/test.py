import kompyle as p
import klay as k

circuit3 = k.Circuit()
print(circuit3.nb_nodes())
nptr1 = p.compile_from_ganak(circuit3, "./assets/toy/toy0.cnf")
circuit3.set_root(nptr1)
print(circuit3.nb_nodes())
nptr2 = p.compile_from_ganak("./assets/toy/toy0.cnf")
circuit3.set_root(nptr2)
print(circuit3.nb_nodes())
nptr = circuit3.or_node([nptr1, nptr2])
print(circuit3.nb_nodes())
circuit3.set_root(nptr)
print(circuit3.get_indices())
