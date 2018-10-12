import unittest

from smrsc.big_step_sc import lazy_mrsc
from smrsc.counters import CountersWorld, CountersScWorld, nw_conf_pp
from smrsc.graph import \
    graph_pretty_printer, cl_empty_and_bad, cl_min_size, unroll
from smrsc.protocols import Synapse


class TestProtocols(unittest.TestCase):
    def run_min_sc(self, cnt: CountersWorld, m: int, d: int):
        name = type(cnt).__name__
        print("\n%s " % name)
        w = CountersScWorld(cnt, m, d)
        l = lazy_mrsc(w, cnt.start())
        sl = cl_empty_and_bad(lambda c: cnt.is_unsafe(*c))(l)
        # len_usl, size_usl = size_unroll(sl)
        # print(len_usl, size_usl)
        ml = cl_min_size(sl)
        mg = unroll(ml)[0]
        print(graph_pretty_printer(mg, cstr=nw_conf_pp))

    def test_Synapse(self):
        self.run_min_sc(Synapse(), 3, 10)


if __name__ == '__main__':
    unittest.main()
