These problem instances were generated using the
CNFgen tool (https://massimolauria.net/cnfgen/). They are
tseitin transformation problems. For each instance, 
you will find the graph (.graph) and the cnf (.cnf).

"A Tseitin formula TSG,c is defined for every undirected
graph G(V,E) and labelling functionc:V→ {0,1}. We introduce
a propositional variable for every edge of G. The Tseitin
formula TSG,c represents a linear system over the field GF(2)
that for every vertex v∈V states that the sum of all edges
adjacent to v equals c(v). A Tseitin formula is satisfiable 
if and only if the sum of values of the labeling function for
all vertices in every connected component is even. The study
of Tseitin formulas is motivated by Proof Complexity. Proof 
Complexity basically deal with unsatisfiable Tseitin formulas 
that roughly speaking encode that it is impossible that a
graph has an odd number of vertices with odd degree - Satisfiable
Tseitin formulas are hard for nondeterministic read-once
branching programs"

# Grid
The graphs form grids of size d x d.
Problems were created using a combination of the following parameters: 
* d = [4..10] : size of grid
* charge = randomeven
using --seed 1

# Random (gnm)
The graphs are randomly generated
(--gnm n m = random graph with n nodes and m random edges)
using a combination of the following parameters:
* n = [120, 125, 130]
* m = [150, 200, 250]
* charde = randomeven
using --seed 1.

# Note
Some of the created instances contained empty clauses
(line only containing 0). They were removed (replace all)
afterwards but the amount of clauses was not always updated.

