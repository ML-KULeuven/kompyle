# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2

import os
import pytest

from util import compile_inline, random_clauses, compile_file

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
toy_path = os.path.join(base_dir, "assets", "toy")


@pytest.fixture
def pair_trivial_sat():
    pair = compile_inline(2, [[1, 2]], "trivial-sat: (x1 OR x2)")
    yield pair
    pair.cleanup()


@pytest.fixture
def pair_trivial_unsat():
    pair = compile_inline(2, [[1], [-1]], "trivial-unsat: x1 AND -x1")
    yield pair
    pair.cleanup()


@pytest.fixture
def pair_tautology():
    pair = compile_inline(3, [], "tautology: no clauses, n=3")
    yield pair
    pair.cleanup()


@pytest.fixture
def pair_xor():
    pair = compile_inline(3, [[1, 2], [-1, -2]], "x1 XOR x2, x3 free")
    yield pair
    pair.cleanup()


@pytest.fixture
def pair_exactly_one():
    clauses = [[1, 2, 3], [-1, -2], [-1, -3], [-2, -3]]
    pair = compile_inline(3, clauses, "exactly one of {x1, x2, x3}")
    yield pair
    pair.cleanup()


@pytest.fixture(params=[
    # NOTE(Ibrahim):
    # clause-to-variable ratio = 3

    (1, 3, 0),
    (1, 3, 1),
    (2, 6, 0),
    (2, 6, 1),
    (3, 9, 0),
    (3, 9, 1),
    (4, 12, 0),
    (4, 12, 1),
    (5, 15, 0),
    (5, 15, 1),
    (6, 18, 0),
    (7, 21, 0),
    # (8, 24, 0),
    # (9, 27, 0),
    # (10, 30, 0),
    # (11, 33, 0),
    # (12, 36, 0),
    # (20, 60, 0),
    # (50, 150, 0),

    # NOTE(Ibrahim):
    # small debug examples

    # (2, 2, 0),
    # (2, 2, 1),
    # (30, 26, 0),
])
def pair_random(request):
    n, m, seed = request.param
    clauses = random_clauses(n, m, k=3, seed=seed)
    pair = compile_inline(n, clauses, f"random-3cnf-n{n}-m{m}-s{seed}")
    yield pair
    pair.cleanup()


@pytest.fixture(params=[
    # NOTE(Ibrahim):
    # clause-to-variable ratio = 3

    # (5, 15, 0),
    # (5, 15, 1),
    # (6, 18, 0),
    # (7, 21, 0),
    # (8, 24, 0),
    # (9, 27, 0),
    # (10, 30, 0),
    # (11, 33, 0),
    # (12, 36, 0),
    # (20, 60, 0),

    # NOTE(Ibrahim):
    # small debug examples
    (2, 2, 0),
    # (2, 2, 1),
    # (30, 26, 0),
    # (30, 90, 0),
    # (40, 120, 0),
    # (50, 150, 0),
])
def pair_random_structure(request):
    n, m, seed = request.param
    clauses = random_clauses(n, m, k=3, seed=seed)
    pair = compile_inline(n, clauses, f"random-3cnf-n{n}-m{m}-s{seed}")
    yield pair
    pair.cleanup()



@pytest.fixture
def pair_toy0():
    path = os.path.join(toy_path, "toy0.cnf")
    if not os.path.exists(path):
        pytest.skip(f"not found: {path}")
    yield compile_file(str(path), "toy0.cnf")


@pytest.fixture
def pair_toy1():
    path = os.path.join(toy_path, "toy1.cnf")
    if not os.path.exists(path):
        pytest.skip(f"not found: {path}")
    yield compile_file(str(path), "toy1.cnf")


@pytest.fixture
def pair_unit_forced():
    clauses = [
        [1],
        [-2],
        [1, 2, 3],
    ]
    pair = compile_inline(3, clauses, "unit-forced: x1=T, x2=F, x3 free")
    yield pair
    pair.cleanup()


@pytest.fixture
def pair_unit_forced_unsat():
    clauses = [
        [1],
        [-1],
    ]
    pair = compile_inline(1, clauses, "unit-forced-unsat: x1=T and x1=F")
    yield pair
    pair.cleanup()


@pytest.fixture
def pair_unit_chain():
    clauses = [
        [1],
        [-1, 2],
        [-2, 3],
    ]
    pair = compile_inline(3, clauses, "unit-chain: x1 -> x2 -> x3, all forced T")
    yield pair
    pair.cleanup()

@pytest.fixture
def pair_unit_cascade_large():
    clauses = []

    clauses.append([1])
    for i in range(1, 15):
        clauses.append([-i, i + 1])

    clauses.append([-19])
    clauses.append([20])

    clauses.append([16, 17, 18])

    pair = compile_inline(20, clauses, "unit-cascade-large")
    yield pair
    pair.cleanup()

@pytest.fixture(params=[
    "pair_trivial_sat",
    "pair_tautology",
    "pair_xor",
    "pair_exactly_one",
])
def sat_pair(request):
    yield request.getfixturevalue(request.param)


@pytest.fixture(params=[
    "pair_trivial_unsat",
])
def unsat_pair(request):
    yield request.getfixturevalue(request.param)


@pytest.fixture(params=[
    "pair_trivial_sat",
    "pair_trivial_unsat",
    "pair_tautology",
    "pair_xor",
    "pair_exactly_one",
])
def any_pair(request):
    yield request.getfixturevalue(request.param)
