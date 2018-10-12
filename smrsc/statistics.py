#
# Counting without generation
#
#
# The main idea of staged supercompilation consists in
# replacing the analysis of residual graphs with the analysis
# of the program that generates the graphs.
#
# Gathering statistics about graphs is just a special case of
# such analysis. For example, it is possible to count the number of
# residual graphs that would be produced without actually generating
# the graphs.
#
# Technically, we can define a function `length_unroll(c)` that analyses
# lazy graphs such that
#   length_unroll(l) == unroll(l).length

from typing import Tuple, List
from numpy import long

from smrsc.graph import LazyGraph, C, Empty, Stop, Build


def length_unroll(l: LazyGraph[C]) -> long:
    if isinstance(l, Empty):
        return 0
    elif isinstance(l, Stop):
        return 1
    elif isinstance(l, Build):
        s: long = 0
        for ls in l.lss:
            m: long = 1
            for l in ls:
                m *= length_unroll(l)
            s += m
        return s
    else:
        raise ValueError
    pass


#
# Counting nodes in collections of graphs
#
# Let us find a function `size_unroll(l)`, such that
#   size_unroll(l) == (unroll(l).length , unroll(l).map(graph_size).sum)
#

def size_unroll(l: LazyGraph[C]) -> Tuple[long, long]:
    if isinstance(l, Empty):
        return 0, 0
    elif isinstance(l, Stop):
        return 1, 1
    elif isinstance(l, Build):
        k: long = 0
        n: long = 0
        for ls in l.lss:
            k1, n1 = size_unroll_ls(ls)
            k, n = k + k1, n + k1 + n1
        return k, n


def size_unroll_ls(ls: List[LazyGraph[C]]) -> Tuple[long, long]:
    k: long = 1
    n: long = 0
    for l in ls:
        k1, n1 = size_unroll(l)
        k, n = k * k1, k * n1 + k1 * n
    return k, n
