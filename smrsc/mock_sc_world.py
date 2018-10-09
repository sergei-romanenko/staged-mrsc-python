from typing import TypeVar, Generic, List
from smrsc.big_step_sc import ScWorld

class MockScWorld(ScWorld[int]):
    History = List[int]
    C = int

    @staticmethod
    def isDangerous(h: History) -> bool:
        return len(h) > 3

    @staticmethod
    def isFoldableTo(c1: C, c2: C) -> bool:
        return c1 == c2

    @staticmethod
    def develop(c: C) -> List[List[C]]:
        return MockScWorld.drive(c) + MockScWorld.rebuild(c)

    @staticmethod
    def drive(c: C) -> List[List[C]]:
        return [] if (c < 2) else [[0, c - 1], [c - 1]]

    @staticmethod
    def rebuild(c: C) -> List[List[C]]:
        return [[c + 1]]
