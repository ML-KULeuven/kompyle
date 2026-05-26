#! /usr/bin/env python
from __future__ import print_function

import time
from problog.formula import LogicDAG
from problog.program import PrologFile
from problog.logic import Term
from problog.engine import DefaultEngine
from problog.cnf_formula import CNF


class Timer(object):
    def __init__(self, msg):
        self.message = msg
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()

    def __exit__(self, *args):
        print("%s: %.4fs" % (self.message, time.time() - self.start_time))


def main(filename, output):

    model = PrologFile(filename)

    engine = DefaultEngine(label_all=True)

    with Timer("parsing"):
        db = engine.prepare(model)

    print("\n=== Database ===")
    print(db)

    print("\n=== Queries ===")
    queries = engine.query(db, Term("query", None))
    print("Queries:", ", ".join([str(q[0]) for q in queries]))

    print("\n=== Evidence ===")
    evidence = engine.query(db, Term("evidence", None, None))
    print("Evidence:", ", ".join(["%s=%s" % ev for ev in evidence]))

    print("\n=== Ground Program ===")
    with Timer("ground"):
        gp = engine.ground_all(db)
    print(gp)

    print("\n=== Acyclic Ground Program ===")
    with Timer("acyclic"):
        gp = LogicDAG.createFrom(gp)
    print(gp)

    print("\n=== Conversion to CNF ===")
    with Timer("convert to CNF"):
        cnf = CNF.createFrom(gp)

    with open(output, "w") as f:
        f.write(cnf.to_dimacs(weighted=False, names=True))


if __name__ == "__main__":
    import argparse

    argparser = argparse.ArgumentParser()
    argparser.add_argument("filename")
    argparser.add_argument("output")
    args = argparser.parse_args()

    main(**vars(args))
