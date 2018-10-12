from typing import List, Tuple, Union

from smrsc.counters import CountersWorld, NW, N, W, w

class Synapse(CountersWorld):
    C = List[Union[NW, int]]

    @staticmethod
    def start() -> C:
        return [w, 0, 0]

    @staticmethod
    def rules(i: NW, d: NW, v: NW) -> List[Tuple[bool, C]]:
        return [
            (i >= 1, [i + d - 1, 0, v + 1]),
            (v >= 1, [i + d + v - 1, 1, 0]),
            (i >= 1, [i + d + v - 1, 1, 0])]

    @staticmethod
    def is_unsafe(i: NW, d: NW, v: NW) -> bool:
        return (d >= 1 and v >= 1) or (d >= 2)
