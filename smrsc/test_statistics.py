import unittest

from smrsc.graph import *
from smrsc.mock_sc_world import *
import smrsc.big_step_sc
from smrsc.statistics import *


def naive_mrsc(c: int):
    return smrsc.big_step_sc.naive_mrsc(MockScWorld(), c)


def lazy_mrsc(c: int):
    return smrsc.big_step_sc.lazy_mrsc(MockScWorld(), c)


l1: LazyGraph[C] = lazy_mrsc(0)
ul1: List[Graph[C]] = unroll(l1)


class BigStepScTests(unittest.TestCase):
    def test_len_unroll(self):
        self.assertEqual(length_unroll(l1), len(ul1))

    def test_size_unroll(self):
        self.assertEqual(
            size_unroll(l1),
            (len(ul1), sum(map(graph_size, ul1))))


if __name__ == '__main__':
    unittest.main()
