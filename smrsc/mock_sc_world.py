from typing import List
from smrsc.big_step_sc import ScWorld

class MockScWorld(ScWorld[int]):
    History = List[int]
    C = int

    def is_dangerous(self, h: History) -> bool:
        return len(h) > 3

    def is_foldable_to(self, c1: C, c2: C) -> bool:
        return c1 == c2

    def develop(self, c: C) -> List[List[C]]:
        return self.drive(c) + self.rebuild(c)

    def drive(self, c: C) -> List[List[C]]:
        return [] if (c < 2) else [[0, c - 1], [c - 1]]

    def rebuild(self, c: C) -> List[List[C]]:
        return [[c + 1]]
