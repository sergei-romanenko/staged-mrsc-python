import unittest
from typing import List, Tuple

from smrsc.graph import Graph, Back, Forth, unroll, cl_min_size, LazyGraph
from smrsc.big_step_sc import naive_mrsc, lazy_mrsc
from smrsc.counters import NW, N, W, CountersScWorld

start = [N(2), N(0)]


def rules(i : NW, j : NW) -> List[Tuple[bool, List[NW]]]:
    return [
        (i >= 1, [i - 1, j + 1]),
        (j >= 1, [i + 1, j - 1])
    ]


def is_unsafe(c: List[NW]) -> bool:
    return False


cnt_world = CountersScWorld(start, rules, is_unsafe, 3, 10)

mg: Graph[List[NW]] = \
    Forth([N(2), N(0)], [
        Forth([W(), W()], [
            Back([W(), W()]),
            Back([W(), W()])])])


class GraphTests(unittest.TestCase):
    def test_naive_mrsc__lazy_mrsc(self):
        gs = naive_mrsc(cnt_world, start)
        # print("gs.length ==%s" % len(gs))
        l: LazyGraph[List[NW]] = lazy_mrsc(cnt_world, start)
        self.assertEqual(unroll(l), gs)
        ml = cl_min_size(l)
        self.assertEqual(unroll(ml)[0], mg)
