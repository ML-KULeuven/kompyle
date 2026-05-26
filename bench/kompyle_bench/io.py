# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2
"""Low-level I/O helpers.

* `silence_fds` / `silenced_fds` temporarily redirect stdout/stderr to
    ``/dev/null`` at the file-descriptor level, so chatty C++ libraries
    called through pybind/nanobind are quiet too.
* `parse_cnf` reads a DIMACS file into a list of clauses.
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Iterator


@contextmanager
def silenced_fds() -> Iterator[None]:
    """Redirect stdout (fd 1) and stderr (fd 2) to /dev/null for the duration
    of the ``with`` block. Restores both fds on exit.

    Use this around C++ backend calls that print directly to fd 1/2.
    """
    devnull = os.open(os.devnull, os.O_WRONLY)
    old_out = os.dup(1)
    old_err = os.dup(2)
    try:
        os.dup2(devnull, 1)
        os.dup2(devnull, 2)
        yield
    finally:
        os.dup2(old_out, 1)
        os.dup2(old_err, 2)
        os.close(devnull)
        os.close(old_out)
        os.close(old_err)


def parse_cnf(path: str | os.PathLike) -> tuple[int, list[list[int]]]:
    """Parse a DIMACS CNF file.

    Returns ``(n_vars, clauses)`` where each clause is a list of signed
    literals (sign indicates polarity, magnitude is the 1-based var id).
    """
    n_vars = 0
    clauses: list[list[int]] = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("c"):
                continue
            if line.startswith("p"):
                n_vars = int(line.split()[2])
                continue
            lits = [int(x) for x in line.split() if x != "0"]
            if lits:
                clauses.append(lits)
    return n_vars, clauses
