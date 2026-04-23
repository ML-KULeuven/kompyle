from pysdd.sdd_c cimport SddNode
from libc.stdint cimport uintptr_t

def _sdd_node_ptr(SddNode node) -> int:
    return <uintptr_t>node._sddnode
