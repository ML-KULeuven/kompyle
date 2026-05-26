Source of these problems:
http://www.cril.univ-artois.fr/PMC/instancesCompilation.tar.gz.

They are very likely the same as these problems:
https://www.cs.rochester.edu/u/kautz/Cachet/Model_Counting_Benchmarks/Grid.zip 
which are accompanied by the following description:

A grid network is an N x N grid, where there are two directed edges
from a node to its neighbors right and down. The upper-left node is 
a source, and the bottom-right node is a sink. The query is to
compute the probability of the sink being true given no evidence. 
The deterministic ratio is a parameter specifying the fraction of nodes
that are deterministic, that is, whose values are determined given the
values of their parents. There are 10 random instances generated for each size.

e.g. 50-10-1-q.cnf -> 50% of the nodes are deterministic, grid is order 10 (10x10 = 100 nodes)

# How to obtain
The software and benchmarks are made available publicly and freely for research
purposes on https://www.cs.rochester.edu/u/kautz/Cachet/Model_Counting_Benchmarks/Grid.zip

The following instances were used to evaluate 
'Symmetric Component Caching for Model Counting on Combinatorial Instances' in AAAI2021 by 
Timothy van Bremen, Vincent Derkinderen, Shubham Sharma, Subhajit Roy, and Kuldeep S. Meel.
They are also the same instances that were used to evaluate ISYMGANAK.

* Ratio_50/50-10-10-q.cnf
* Ratio_50/50-10-6-q.cnf
* Ratio_50/50-12-3-q.cnf
* Ratio_50/50-12-4-q.cnf
* Ratio_50/50-12-6-q.cnf
* Ratio_50/50-14-5-q.cnf
* Ratio_50/50-14-9-q.cnf
* Ratio_50/50-16-10-q.cnf
* Ratio_50/50-16-7-q.cnf
* Ratio_50/50-18-2-q.cnf

* Ratio_75/75-10-7-q.cnf
* Ratio_75/75-12-10-q.cnf
* Ratio_75/75-16-5-q.cnf
* Ratio_75/75-18-5-q.cnf
* Ratio_75/75-21-5-q.cnf
* Ratio_75/75-21-7-q.cnf
* Ratio_75/75-22-6-q.cnf
* Ratio_75/75-23-3-q.cnf
* Ratio_75/75-24-8-q.cnf
* Ratio_75/75-26-1-q.cnf

* Ratio_90/90-14-6-q.cnf
* Ratio_90/90-15-3-q.cnf
* Ratio_90/90-17-7-q.cnf
* Ratio_90/90-17-8-q.cnf
* Ratio_90/90-18-1-q.cnf
* Ratio_90/90-18-9-q.cnf
* Ratio_90/90-19-10-q.cnf
* Ratio_90/90-23-10-q.cnf
* Ratio_90/90-26-1-q.cnf
* Ratio_90/90-50-6-q.cnf
