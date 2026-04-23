def sdd_to_klay(circuit, node):
    cache = {}
    return _sdd_to_klay(node, circuit, cache)

def _sdd_to_klay(node, circuit, cache):
    if node in cache:
        return cache[node]

    if node.is_true():
        result = circuit.true_node()

    elif node.is_false():
        result = circuit.false_node()

    elif node.is_literal():
        result = circuit.literal_node(node.literal)

    elif node.is_decision():
        or_children = []
        for prime, sub in node.elements():
            klay_prime = _sdd_to_klay(prime, circuit, cache)
            klay_sub = _sdd_to_klay(sub, circuit, cache)
            and_child = circuit.and_node([klay_prime, klay_sub])
            or_children.append(and_child)
        result = circuit.or_node(or_children)

    else:
        raise RuntimeError("Unrecognizable SddNode")

    cache[node] = result
    return result
