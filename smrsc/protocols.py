from typing import List, Tuple

from smrsc.counters import CountersWorld, NW, N, W

class Synapse(CountersWorld):
    C = List[NW]

    @staticmethod
    def start() -> C:
        return [W(), N(0), N(0)]

    @staticmethod
    def rules(i: NW, d: NW, v: NW) -> List[Tuple[bool, C]]:
        return [
            (i >= 1, [i + d - 1, N(0), v + 1]),
            (v >= 1, [i + d + v - 1, N(1), N(0)]),
            (i >= 1, [i + d + v - 1, N(1), N(0)])]

    @staticmethod
    def is_unsafe(i: NW, d: NW, v: NW) -> bool:
        return (d >= 1 and v >= 1) or (d >= 2)
