import unittest
from typing import List, Tuple

from smrsc.graph import Graph, Back, Forth, unroll, cl_min_size, LazyGraph
from smrsc.big_step_sc import naive_mrsc, lazy_mrsc
from smrsc.counters import NW, N, W, CountersWorld, CountersScWorld


class TestCountersWorld(CountersWorld):
    C = CountersWorld.C

    @staticmethod
    def start() -> C:
        return [N(2), N(0)]

    @staticmethod
    def rules(i: NW, j: NW) -> List[Tuple[bool, C]]:
        return [
            (i >= 1, [i - 1, j + 1]),
            (j >= 1, [i + 1, j - 1])]

    @staticmethod
    def is_unsafe(*nw: NW) -> bool:
        return False


mg: Graph[List[NW]] = \
    Forth([N(2), N(0)], [
        Forth([W(), W()], [
            Back([W(), W()]),
            Back([W(), W()])])])

w = CountersScWorld(TestCountersWorld(), 3, 10)


class GraphTests(unittest.TestCase):

    def test_naive_mrsc__lazy_mrsc(self):
        gs = naive_mrsc(w, w.cnt.start())
        # print("gs.length ==%s" % len(gs))
        l: LazyGraph[List[NW]] = lazy_mrsc(w, w.cnt.start())
        self.assertEqual(unroll(l), gs)
        ml = cl_min_size(l)
        self.assertEqual(unroll(ml)[0], mg)


if __name__ == '__main__':
    unittest.main()
