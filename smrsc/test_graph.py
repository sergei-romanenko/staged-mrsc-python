import unittest

from smrsc.graph import *


def ibad(c):
    return c < 0


g1 = \
    Forth(1, [
        Back(1),
        Forth(2, [
            Back(1),
            Back(2)])])

g_bad_forth = \
    Forth(1, [
        Back(1),
        Forth(-2, [
            Back(3),
            Back(4)])])

g_bad_back = \
    Forth(1, [
        Back(1),
        Forth(2, [
            Back(3),
            Back(-4)])])

l2 = \
    Build(1, [
        [Build(2, [[Stop(1), Stop(2)]])],
        [Build(3, [[Stop(3), Stop(1)]])]])

gs2 = [Forth(1, [Forth(2, [Back(1), Back(2)])]),
       Forth(1, [Forth(3, [Back(3), Back(1)])])]

l_empty = \
    Build(1, [
        [Stop(2)],
        [Build(3, [
            [Stop(4), Empty()]])]])

l_bad_forth = \
    Build(1, [
        [Stop(1),
         Build(-2, [
             [Stop(3), Stop(4)]])]])

l_bad_back = \
    Build(1, [
        [Stop(1),
         Build(2, [
             [Stop(3),
              Stop(-4)]])]])

l3 = \
    Build(1, [
        [Build(2, [
            [Stop(1), Stop(2)]])],
        [Build(3, [
            [Stop(4)]])]])


class GraphTests(unittest.TestCase):

    def test_cartesian(self):
        self.assertEqual(cartesian(((), (10, 20))), [])
        self.assertEqual(cartesian(((1, 2), ())), [])
        self.assertEqual(
            cartesian([[1, 2], [10, 20]]),
            [[1, 10], [1, 20], [2, 10], [2, 20]])

    def test_unroll_Empty(self):
        self.assertEqual(unroll(Empty()), [])

    def test_unroll_Stop(self):
        self.assertEqual(unroll(Stop(100)), [Back(100)])

    def test_unroll(self):
        self.assertEqual(unroll(l2), gs2)

    def test_not_bad(self):
        self.assertFalse(bad_graph(ibad)(g1))

    def test_bad_forth(self):
        self.assertTrue(bad_graph(ibad)(g_bad_forth))

    def test_bad_back(self):
        self.assertTrue(bad_graph(ibad)(g_bad_back))

    def test_cl_empty(self):
        self.assertEqual(cl_empty(l_empty), Build(1, [[Stop(2)]]))

    def test_lazy_bad_forth(self):
        self.assertEqual(
            cl_bad_conf(ibad)(l_bad_forth),
            Build(1, [[Stop(1), Empty()]]))

    def test_lazy_bad_forth_cl(self):
        self.assertEqual(cl_empty_and_bad(ibad)(l_bad_forth),
                         Empty())

    def test_lazy_bad_back(self):
        self.assertEqual(
            cl_bad_conf(ibad)(l_bad_back),
            Build(1, [[Stop(1), Build(2, [[Stop(3), Empty()]])]]))

    def test_lazy_bad_back_cl(self):
        self.assertEqual(
            cl_empty_and_bad(ibad)(l_bad_back),
            Empty())

    def test_graph_size(self):
        self.assertEqual(graph_size(g1), 5)

    def test_min_size_cl(self):
        self.assertEqual(
            cl_min_size(l3),
            Build(1, [
                [Build(3, [
                    [Stop(4)]])]]))

    def test_min_size_cl_unroll(self):
        min_l = cl_min_size(l3)
        min_g = unroll(min_l)[0]
        self.assertEqual(
            min_g,
            Forth(1, [
                Forth(3, [
                    Back(4)])]))


if __name__ == '__main__':
    unittest.main()
