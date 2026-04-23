from bench_sdd_compile import random_clauses, write_dimacs
from kompyle import Circuit, compile_from_cnf_using_sdd


name = "tmp.cnf"
n_vars = 50
clauses = random_clauses(n_vars, n_clauses=150, k=3, seed=1)
write_dimacs(name, clauses, n_vars)

# compare heap usage/memory usage
# valgrind --tool=massif --pages-as-heap=yes python your_script.py
# pip install gprof2dot
# massif-visualizer massif.out.<pid>

circuit = Circuit()
result = compile_from_cnf_using_sdd(circuit, name)
# result already in klay circuit
