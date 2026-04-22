# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2

import os
import torch
import kompyle as p

from util import (
    cnf_to_gated_formula,
    compile_gated,
    compile_inline,
    random_clauses,
    write_cnf,
    all_assignments,
    eval_formula,
    COMPILER_IDS,
    COMPILER_FUNCS,
)


# ===================================================================
# HELPERS
# ===================================================================

def compile_gf_into(circuit: p.Circuit, n_vars: int, clauses) -> p.NodePtr:
    gf = cnf_to_gated_formula(n_vars, clauses)
    return p.compile_from_gates_formula_using_d4v2(circuit, gf)


def eval_roots(circuit: p.Circuit, n_total_vars: int, alpha: dict) -> list:
    pos_w = torch.tensor(
        [1.0 if alpha[v + 1] else 0.0 for v in range(n_total_vars)]
    )
    m = circuit.to_torch_module(semiring="real")
    result = m(pos_w)
    return [float(result[i]) > 0.5 for i in range(len(result))]


def make_circuit() -> p.Circuit:
    return p.Circuit()

def make_or_gf(input_names, gate_name="g_out"):
    gf = p.GatedFormula()
    for v in input_names:
        gf.add_input(v)
    gf.add_or(gate_name, list(input_names))
    gf.add_target(gate_name)
    return gf

def make_and_gf(input_names, gate_name="g_out"):
    gf = p.GatedFormula()
    for v in input_names:
        gf.add_input(v)
    gf.add_and(gate_name, list(input_names))
    gf.add_target(gate_name)
    return gf


# ===================================================================
# 1. STRUCTURAL INVARIANTS
# ===================================================================

class TestSequentialCompilationStructure:
    def test_sequential_roots_accumulate(self):
        circuit = make_circuit()
        formula_specs = [
            (2, [[1, 2]]),
            (2, [[1], [-2]]),
            (3, [[1, 2], [-1, -2]]),
        ]
        for i, (n, clauses) in enumerate(formula_specs):
            root = compile_gf_into(circuit, n, clauses)
            circuit.set_root(root)
            assert circuit.nb_root_nodes() == i + 1

    def test_identical_formula_reuses_nodes(self):
        circuit = make_circuit()
        n_vars, clauses = 3, [[1, 2], [-1, -2]]

        root_a = compile_gf_into(circuit, n_vars, clauses)
        circuit.set_root(root_a)
        nb_after_first = circuit.nb_nodes()

        root_b = compile_gf_into(circuit, n_vars, clauses)
        circuit.set_root(root_b)
        nb_after_second = circuit.nb_nodes()

        assert nb_after_second == nb_after_first, (
            "Recompiling the same formula must not add new nodes"
        )
        assert circuit.nb_root_nodes() == 2

    def test_distinct_formula_grows_circuit(self):
        circuit = make_circuit()

        root_a = compile_gf_into(circuit, 3, [[1, 2], [-1, -2]])
        circuit.set_root(root_a)
        nb_after_first = circuit.nb_nodes()

        root_b = compile_gf_into(circuit, 3, [[1, 2, 3]])
        circuit.set_root(root_b)
        nb_after_second = circuit.nb_nodes()

        assert nb_after_second >= nb_after_first

    def test_remove_unused_nodes_preserves_roots(self):
        circuit = make_circuit()
        for n, clauses in [(2, [[1, 2]]), (3, [[1, 2], [-1, -2]])]:
            root = compile_gf_into(circuit, n, clauses)
            circuit.set_root(root)

        nb_before = circuit.nb_nodes()
        circuit.remove_unused_nodes()

        assert circuit.nb_root_nodes() == 2
        assert circuit.nb_nodes() <= nb_before


# ===================================================================
# 2. VARIABLE-NAME / INDEX MAPPING
# ===================================================================

class TestVariableMapping:
    def test_permuted_declaration_order_correct_truth_table(self):
        gf = p.GatedFormula()
        gf.add_input("x2")
        gf.add_input("x1")
        gf.add_and("g", ["x2", "x1"])
        gf.add_target("g")

        circuit = make_circuit()
        root = p.compile_from_gates_formula_using_d4v2(circuit, gf)
        circuit.set_root(root)

        expected_and = {
            (False, False): False,
            (False, True):  False,
            (True,  False): False,
            (True,  True):  True,
        }
        for alpha in all_assignments(2):
            vals = eval_roots(circuit, 2, alpha)
            x1, x2 = alpha[1], alpha[2]
            assert vals[0] == expected_and[(x1, x2)], (
                f"permuted AND: x1={x1}, x2={x2} -> "
                f"expected {expected_and[(x1,x2)]}, got {vals[0]}"
            )

    def test_permuted_and_normal_order_agree(self):
        gf_normal = p.GatedFormula()
        gf_normal.add_input("x1")
        gf_normal.add_input("x2")
        gf_normal.add_and("g_n", ["x1", "x2"])
        gf_normal.add_target("g_n")

        gf_reversed = p.GatedFormula()
        gf_reversed.add_input("x2")
        gf_reversed.add_input("x1")
        gf_reversed.add_and("g_r", ["x2", "x1"])
        gf_reversed.add_target("g_r")

        circuit = make_circuit()
        root_n = p.compile_from_gates_formula_using_d4v2(circuit, gf_normal)
        root_r = p.compile_from_gates_formula_using_d4v2(circuit, gf_reversed)
        circuit.set_root(root_n)
        circuit.set_root(root_r)

        for alpha in all_assignments(2):
            vals = eval_roots(circuit, 2, alpha)
            assert vals[0] == vals[1], (
                f"Normal vs. reversed-order AND disagree at {alpha}: "
                f"normal={vals[0]}, reversed={vals[1]}"
            )

    def test_permuted_or_and_normal_order_agree(self):
        gf_normal = p.GatedFormula()
        gf_normal.add_input("x1")
        gf_normal.add_input("x2")
        gf_normal.add_or("g_n", ["x1", "x2"])
        gf_normal.add_target("g_n")

        gf_reversed = p.GatedFormula()
        gf_reversed.add_input("x2")
        gf_reversed.add_input("x1")
        gf_reversed.add_or("g_r", ["x2", "x1"])
        gf_reversed.add_target("g_r")

        circuit = make_circuit()
        root_n = p.compile_from_gates_formula_using_d4v2(circuit, gf_normal)
        root_r = p.compile_from_gates_formula_using_d4v2(circuit, gf_reversed)
        circuit.set_root(root_n)
        circuit.set_root(root_r)

        for alpha in all_assignments(2):
            vals = eval_roots(circuit, 2, alpha)
            assert vals[0] == vals[1], (
                f"Normal vs. reversed-order OR disagree at {alpha}: "
                f"normal={vals[0]}, reversed={vals[1]}"
            )

    def test_disjoint_variable_names_correct_inference(self):
        circuit = make_circuit()

        gf_a = make_and_gf(["x1", "x2"], gate_name="g_a")
        root_a = p.compile_from_gates_formula_using_d4v2(circuit, gf_a)
        circuit.set_root(root_a)

        gf_b = make_or_gf(["x3", "x4"], gate_name="g_b")
        root_b = p.compile_from_gates_formula_using_d4v2(circuit, gf_b)
        circuit.set_root(root_b)

        assert circuit.nb_root_nodes() == 2

        for alpha in all_assignments(5):
            vals = eval_roots(circuit, 5, alpha)
            expected_a = alpha[1] and alpha[2]
            expected_b = alpha[4] or  alpha[5]
            assert vals[0] == expected_a, (
                f"Formula A (x1 AND x2) wrong at {alpha}: "
                f"expected {expected_a}, got {vals[0]}"
            )
            assert vals[1] == expected_b, (
                f"Formula B (x3 OR x4) wrong at {alpha}: "
                f"expected {expected_b}, got {vals[1]}"
            )


class TestMultiFormulaInference:
    def test_three_formulas_shared_variable_space(self):
        formula_specs = [
            (2, [[1, 2]],           "trivial-sat"),
            (2, [[1], [-2]],        "unit-forced"),
            (3, [[1, 2], [-1, -2]], "xor"),
        ]
        circuit = make_circuit()
        for n, clauses, _ in formula_specs:
            root = compile_gf_into(circuit, n, clauses)
            circuit.set_root(root)

        n_total = 3
        for alpha in all_assignments(n_total):
            vals = eval_roots(circuit, n_total, alpha)
            for i, (n_vars, clauses, desc) in enumerate(formula_specs):
                sub_alpha = {v: alpha[v] for v in range(1, n_vars + 1)}
                expected = eval_formula(clauses, sub_alpha)
                assert vals[i] == expected, (
                    f"[{desc}] wrong at {alpha}: expected {expected}, got {vals[i]}"
                )

    def test_formula_after_duplicate_still_correct(self):
        n_vars    = 3
        clauses_a = [[1, 2], [-1, -2]]
        clauses_b = [[1, 2, 3]]

        circuit = make_circuit()
        root_a1 = compile_gf_into(circuit, n_vars, clauses_a)
        circuit.set_root(root_a1)
        root_a2 = compile_gf_into(circuit, n_vars, clauses_a)
        circuit.set_root(root_a2)
        root_b  = compile_gf_into(circuit, n_vars, clauses_b)
        circuit.set_root(root_b)

        for alpha in all_assignments(n_vars):
            vals    = eval_roots(circuit, n_vars, alpha)
            exp_a   = eval_formula(clauses_a, alpha)
            exp_b   = eval_formula(clauses_b, alpha)
            assert vals[0] == exp_a, (
                f"root_a1 wrong at {alpha}: expected {exp_a}, got {vals[0]}")
            assert vals[1] == exp_a, (
                f"root_a2 wrong at {alpha}: expected {exp_a}, got {vals[1]}")
            assert vals[2] == exp_b, (
                f"root_b  wrong at {alpha}: expected {exp_b}, got {vals[2]}")

    def test_random_formulas_shared_circuit(self):
        random_specs = [
            (3, 9,  0),
            (3, 9,  1),
            (4, 12, 0),
        ]
        compiled = []
        circuit  = make_circuit()
        for n, m, seed in random_specs:
            clauses = random_clauses(n, m, k=3, seed=seed)
            root    = compile_gf_into(circuit, n, clauses)
            circuit.set_root(root)
            compiled.append((n, clauses))

        n_total = max(n for n, _ in compiled)
        for alpha in all_assignments(n_total):
            vals = eval_roots(circuit, n_total, alpha)
            for i, (n_vars, clauses) in enumerate(compiled):
                sub_alpha = {v: alpha[v] for v in range(1, n_vars + 1)}
                expected  = eval_formula(clauses, sub_alpha)
                assert vals[i] == expected, (
                    f"random formula [{i}] (n={n_vars}) wrong at {alpha}: "
                    f"expected {expected}, got {vals[i]}"
                )

    def test_many_formulas_grow_and_infer(self):
        specs = [
            (2, [[1, 2]]),
            (2, [[-1, 2]]),
            (2, [[1, -2]]),
            (2, [[-1, -2]]),
            (2, [[1], [2]]),
        ]
        circuit = make_circuit()
        prev_nb = 0
        for n, clauses in specs:
            root = compile_gf_into(circuit, n, clauses)
            circuit.set_root(root)
            assert circuit.nb_nodes() >= prev_nb
            prev_nb = circuit.nb_nodes()

        for alpha in all_assignments(2):
            vals = eval_roots(circuit, 2, alpha)
            for i, (n_vars, clauses) in enumerate(specs):
                expected = eval_formula(clauses, alpha)
                assert vals[i] == expected, (
                    f"formula [{i}] wrong at {alpha}: "
                    f"expected {expected}, got {vals[i]}"
                )


class TestCombinedCircuit:
    def test_or_node_correct_inference(self):
        n_vars    = 3
        clauses_a = [[1, 2]]
        clauses_b = [[3]]

        circuit  = make_circuit()
        root_a   = compile_gf_into(circuit, n_vars, clauses_a)
        root_b   = compile_gf_into(circuit, n_vars, clauses_b)
        root_or  = circuit.or_node([root_a, root_b])
        circuit.set_root(root_or)

        for alpha in all_assignments(n_vars):
            vals     = eval_roots(circuit, n_vars, alpha)
            expected = eval_formula(clauses_a, alpha) or eval_formula(clauses_b, alpha)
            assert vals[0] == expected, (
                f"OR combination wrong at {alpha}: expected {expected}, got {vals[0]}"
            )

    def test_or_of_contradictory_formulas_is_tautology(self):
        n_vars   = 1
        circuit  = make_circuit()
        root_pos = compile_gf_into(circuit, n_vars, [[1]])
        root_neg = compile_gf_into(circuit, n_vars, [[-1]])
        root_or  = circuit.or_node([root_pos, root_neg])
        circuit.set_root(root_or)

        for alpha in all_assignments(n_vars):
            vals = eval_roots(circuit, n_vars, alpha)
            assert vals[0] == True, (
                f"x1 OR NOT x1 must always be True; got False at {alpha}"
            )

    def test_and_node_correct_inference(self):
        n_vars    = 3
        clauses_a = [[1, 2]]
        clauses_b = [[-1, 3]]

        circuit  = make_circuit()
        root_a   = compile_gf_into(circuit, n_vars, clauses_a)
        root_b   = compile_gf_into(circuit, n_vars, clauses_b)
        root_and = circuit.and_node([root_a, root_b])
        circuit.set_root(root_and)

        for alpha in all_assignments(n_vars):
            vals     = eval_roots(circuit, n_vars, alpha)
            expected = eval_formula(clauses_a, alpha) and eval_formula(clauses_b, alpha)
            assert vals[0] == expected, (
                f"AND combination wrong at {alpha}: expected {expected}, got {vals[0]}"
            )

    def test_and_of_contradictory_formulas_is_unsat(self):
        n_vars   = 1
        circuit  = make_circuit()
        root_pos = compile_gf_into(circuit, n_vars, [[1]])   # x1
        root_neg = compile_gf_into(circuit, n_vars, [[-1]])  # NOT x1
        root_and = circuit.and_node([root_pos, root_neg])
        circuit.set_root(root_and)

        for alpha in all_assignments(n_vars):
            vals = eval_roots(circuit, n_vars, alpha)
            assert vals[0] == False, (
                f"x1 AND NOT x1 must always be False; got True at {alpha}"
            )

    def test_nested_or_then_and(self):
        n_vars    = 3
        clauses_a = [[1]]
        clauses_b = [[2]]
        clauses_c = [[1, 2, 3]]

        circuit  = make_circuit()
        root_a   = compile_gf_into(circuit, n_vars, clauses_a)
        root_b   = compile_gf_into(circuit, n_vars, clauses_b)
        root_c   = compile_gf_into(circuit, n_vars, clauses_c)
        root_ab  = circuit.or_node([root_a, root_b])
        root_res = circuit.and_node([root_ab, root_c])
        circuit.set_root(root_res)

        for alpha in all_assignments(n_vars):
            vals     = eval_roots(circuit, n_vars, alpha)
            fa, fb, fc = (eval_formula(c, alpha)
                          for c in [clauses_a, clauses_b, clauses_c])
            expected = (fa or fb) and fc
            assert vals[0] == expected, (
                f"(A OR B) AND C wrong at {alpha}: expected {expected}, got {vals[0]}"
            )

    def test_nested_and_then_or(self):
        n_vars    = 3
        clauses_a = [[1, 2]]
        clauses_b = [[3]]
        clauses_c = [[-3]]

        circuit  = make_circuit()
        root_a   = compile_gf_into(circuit, n_vars, clauses_a)
        root_b   = compile_gf_into(circuit, n_vars, clauses_b)
        root_c   = compile_gf_into(circuit, n_vars, clauses_c)
        root_bc  = circuit.or_node([root_b, root_c])
        root_res = circuit.and_node([root_a, root_bc])
        circuit.set_root(root_res)

        for alpha in all_assignments(n_vars):
            vals     = eval_roots(circuit, n_vars, alpha)
            expected = eval_formula(clauses_a, alpha)
            assert vals[0] == expected, (
                f"A AND (B OR C) wrong at {alpha}: expected {expected}, got {vals[0]}"
            )

    def test_independent_roots_plus_combined_root(self):
        n_vars    = 3
        clauses_a = [[1, 2]]
        clauses_b = [[3]]

        circuit  = make_circuit()
        root_a   = compile_gf_into(circuit, n_vars, clauses_a)
        root_b   = compile_gf_into(circuit, n_vars, clauses_b)
        root_or  = circuit.or_node([root_a, root_b])

        circuit.set_root(root_a)
        circuit.set_root(root_b)
        circuit.set_root(root_or)
        assert circuit.nb_root_nodes() == 3

        for alpha in all_assignments(n_vars):
            vals = eval_roots(circuit, n_vars, alpha)
            fa   = eval_formula(clauses_a, alpha)
            fb   = eval_formula(clauses_b, alpha)
            assert vals[0] == fa,         f"root_a wrong at {alpha}"
            assert vals[1] == fb,         f"root_b wrong at {alpha}"
            assert vals[2] == (fa or fb), f"root_or wrong at {alpha}"


class TestCrossCompilerConsistency:
    def test_gated_vs_each_cnf_backend(self):
        n_vars  = 3
        clauses = [[1, 2], [-1, -2]]

        gf_pair = compile_gated(n_vars, clauses, "xor-gated")

        for cid, cfn in zip(COMPILER_IDS, COMPILER_FUNCS):
            cnf_pair = compile_inline(n_vars, clauses, f"xor-{cid}", cfn, cid)
            for alpha in all_assignments(n_vars):
                gf_val  = eval_roots(gf_pair.circuit,  n_vars, alpha)[0]
                cnf_val = eval_roots(cnf_pair.circuit, n_vars, alpha)[0]
                assert gf_val == cnf_val, (
                    f"GatedFormula vs {cid} disagree at {alpha}: "
                    f"gated={gf_val}, {cid}={cnf_val}"
                )
            cnf_pair.cleanup()

    def test_all_backends_in_same_circuit_agree(self):
        n_vars   = 3
        clauses  = [[1, 2], [-1, -2]]
        cnf_path = write_cnf(n_vars, clauses)

        circuit       = make_circuit()
        backend_names = []

        gf   = cnf_to_gated_formula(n_vars, clauses)
        root = p.compile_from_gates_formula_using_d4v2(circuit, gf)
        circuit.set_root(root)
        backend_names.append("gates_d4v2")

        for cid, cfn in zip(COMPILER_IDS, COMPILER_FUNCS):
            root = cfn(circuit, cnf_path)
            circuit.set_root(root)
            backend_names.append(cid)

        os.unlink(cnf_path)

        for alpha in all_assignments(n_vars):
            vals       = eval_roots(circuit, n_vars, alpha)
            mismatches = [
                f"{backend_names[i]}={vals[i]}"
                for i in range(len(vals))
                if vals[i] != vals[0]
            ]
            assert not mismatches, (
                f"Backends disagree at {alpha}: "
                f"{backend_names[0]}={vals[0]}, "
                f"disagreements: {mismatches}"
            )
