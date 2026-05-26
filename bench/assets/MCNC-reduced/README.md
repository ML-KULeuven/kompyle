These problems were obtained from the
[LGSynth91 benchmark](http://web.archive.org/web/20191103092508/https://ddd.fit.cvut.cz/prj/Benchmarks/). 
Primarily meant for logic synthesis and optimization.

The files in the original benchmark were in .blif format,
blif2cnf.pl was used to transform them to DIMAC format.
The source of this script is
[here](https://web.archive.org/web/20050217212056/sat.inesc-id.pt/~jpms/scripts/bin/blif2cnf).

Any CNF that was finished in less than 10s using the GANAK
model counter has been removed, resulting in only the following files:

* apex5.cnf
* apex6.cnf
* C499.cnf
* C880.cnf
* C1355.cnf
* C1908.cnf
* C2670.cnf
* C3540.cnf
* C5315.cnf
* C6288.cnf
* C7552.cnf
* pair.cnf
* t481.cnf
* term1.cnf
* too_large.cnf
* x1.cnf
* x3.cnf

The problem instances dataset is a collection of public benchmarks
that is made available for research purposes by the respective authors.

```bash
$ wget https://ddd.fit.cvut.cz/www/prj/Benchmarks/MCNC.7z

$ 7z e MCNC.7z MCNC/Combinational/blif/apex5.blif MCNC/Combinational/blif/apex6.blif \
MCNC/Combinational/blif/C499.blif MCNC/Combinational/blif/C880.blif \
MCNC/Combinational/blif/C1355.blif MCNC/Combinational/blif/C1908.blif \
MCNC/Combinational/blif/C2670.cnf MCNC/Combinational/blif/C3540.cnf \
MCNC/Combinational/blif/C5315.cnf MCNC/Combinational/blif/C6288.cnf \
MCNC/Combinational/blif/C7552.cnf MCNC/Combinational/blif/pair.blif \
MCNC/Combinational/blif/t481.blif MCNC/Combinational/blif/term1.blif \
MCNC/Combinational/blif/too_large.blif MCNC/Combinational/blif/x1.blif \
MCNC/Combinational/blif/x3.blif

$ perl blif2cnf.sh apex5.blif apex6.blif C1355.blif C1908.blif  \
C499.blif C880.blif pair.blif t481.blif term1.blif too_large.blif \
x1.blif x3.blif
```
