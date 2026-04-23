from bench_sdd_compile import random_clauses, write_dimacs
from pysdd.sdd import SddManager
from kompyle import Circuit, compile_from_sdd_py


name = "tmp.cnf"
n_vars = 100
clauses = random_clauses(n_vars, n_clauses=300, k=3, seed=1)
write_dimacs(name, clauses, n_vars)

# compare heap usage/memory usage
# valgrind --tool=massif --pages-as-heap=yes python your_script.py
# pip install gprof2dot
# massif-visualizer massif.out.<pid>

circuit = Circuit()
_, result = SddManager.from_cnf_file(b'tmp.cnf')
compile_from_sdd_py(circuit, result)  # to transform to klay
