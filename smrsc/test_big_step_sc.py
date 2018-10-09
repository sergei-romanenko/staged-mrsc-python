import unittest
from smrsc.graph import *
from smrsc.mock_sc_world import *
import smrsc.big_step_sc

gs3 = \
    [Forth(0, [Forth(1, [Forth(2, [Back(0), Back(1)])])]),
     Forth(0, [Forth(1, [Forth(2, [Back(1)])])]),
     Forth(0, [Forth(1, [Forth(2, [Forth(3, [Back(0), Back(2)])])])]),
     Forth(0, [Forth(1, [Forth(2, [Forth(3, [Back(2)])])])])]


def naive_mrsc(c: int):
    return smrsc.big_step_sc.naive_mrsc(MockScWorld(), c)


def lazy_mrsc(c: int):
    return smrsc.big_step_sc.lazy_mrsc(MockScWorld(), c)


class BigStepScTests(unittest.TestCase):
    def test_naive_mrsc(self):
        self.assertEqual(naive_mrsc(0), gs3)

    def test_lazy_mrsc(self):
        self.assertEqual(unroll(lazy_mrsc(0)), gs3)

    def test_min_size_cl(self):
        self.assertEqual(
            unroll(cl_min_size(lazy_mrsc(0))),
            [Forth(0, [Forth(1, [Forth(2, [Back(1)])])])])
