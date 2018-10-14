import unittest

from smrsc.big_step_sc8 import *
from smrsc.counters import \
    CountersWorld, CountersScWorld, nw_conf_pp, norm_nw_conf
from smrsc.graph import \
    graph_pretty_printer, cl_empty_and_bad, cl_min_size, unroll
from smrsc.protocols import *
from smrsc.statistics import size_unroll


class TestProtocols8(unittest.TestCase):
    def run_min_sc(self, cnt: CountersWorld, m: int, d: int):
        name = type(cnt).__name__
        print("\n%s " % name, end="")
        w = CountersScWorld(cnt, m, d)
        l8 = build_cograph(w, w.start)
        sl8 = cl8_bad_conf(w.is_unsafe)(l8)
        sl = prune(w, sl8)
        len_usl, size_usl = size_unroll(sl)
        print("(%s, %s)" % (len_usl, size_usl))
        ml = cl_min_size(sl)
        mg = unroll(ml)[0]
        print(graph_pretty_printer(mg, cstr=nw_conf_pp))

    def test_Synapse(self):
        self.run_min_sc(Synapse(), 3, 10)

    def test_MSI(self):
        self.run_min_sc(MSI(), 3, 10)

    def test_MOSI(self):
        self.run_min_sc(MOSI(), 3, 10)

    def test_ReaderWriter(self):
        self.run_min_sc(ReaderWriter(), 3, 5)

    def test_MESI(self):
        self.run_min_sc(MESI(), 3, 10)

    def test_MOESI(self):
        self.run_min_sc(MOESI(), 3, 10)

    def test_Illinois(self):
        self.run_min_sc(Illinois(), 3, 10)

    def test_Berkley(self):
        self.run_min_sc(Berkley(), 3, 10)

    def test_Firefly(self):
        self.run_min_sc(Firefly(), 3, 10)

    # @unittest.skip("Too slow")
    # def test_Futurebus(self):
    #     self.run_min_sc(Futurebus(), 3, 5)

    def test_Xerox(self):
        self.run_min_sc(Xerox(), 3, 10)

    def test_DataRace(self):
        self.run_min_sc(DataRace(), 3, 10)


if __name__ == '__main__':
    unittest.main()
