from abc import ABC, abstractmethod
from typing import List, Tuple

from smrsc.graph import cartesian
from smrsc.big_step_sc import ScWorld


class NW(ABC):
    # @abstractmethod
    def __eq__(self, other) -> bool:
        pass

    # @abstractmethod
    def __add__(self, other):
        pass

    # @abstractmethod
    def __sub__(self, other):
        pass

    # @abstractmethod
    def __ge__(self, other):
        pass

    # @abstractmethod
    def is_eq(self, nw) -> bool:
        pass

    # @abstractmethod
    def is_in(self, nw) -> bool:
        pass


class N(NW):
    def __init__(self, i: int):
        self.i = i

    def __eq__(self, other) -> bool:
        if isinstance(other, N):
            return self.i == other.i
        else:
            return False

    def __add__(self, other) -> NW:
        if isinstance(other, W):
            return W()
        elif isinstance(other, N):
            return N(self.i + other.i)
        elif isinstance(other, int):
            return N(self.i + other)
        else:
            raise ValueError

    def __sub__(self, other) -> NW:
        if isinstance(other, W):
            return W()
        elif isinstance(other, N):
            return N(self.i - other.i)
        elif isinstance(other, int):
            return N(self.i - other)
        else:
            raise ValueError

    def __ge__(self, other) -> bool:
        if isinstance(other, int):
            return self.i >= other
        else:
            raise ValueError

    def is_eq(self, other) -> bool:
        if isinstance(other, int):
            return self.i == other
        else:
            raise ValueError

    def is_in(self, nw: NW) -> bool:
        if isinstance(nw, W):
            return True
        elif isinstance(nw, N):
            return self.i == nw.i
        else:
            raise ValueError

    def __str__(self):
        return str(self.i)

    def __repr__(self):
        return "N(%s)" % self.i


class W(NW):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(W, cls).__new__(cls)
        return cls.instance

    def __eq__(self, other) -> bool:
        return isinstance(other, W)

    def __add__(self, other) -> NW:
        return W()

    def __sub__(self, other) -> NW:
        return W()

    def __ge__(self, other) -> bool:
        if isinstance(other, int):
            return True
        else:
            raise ValueError

    def is_eq(self, other) -> bool:
        if isinstance(other, int):
            return True
        else:
            raise ValueError

    def is_in(self, other) -> bool:
        return isinstance(other, W)

    def __str__(self):
        return "ω"

    def __repr__(self):
        return "W()"


def nw_conf_pp(c: List[NW]):
    return "(" + ", ".join(map(str, c)) + ")"

class CountersWorld(ABC):
    C = List[NW]

    @staticmethod
    @abstractmethod
    def start() -> C:
        pass

    @staticmethod
    @abstractmethod
    def rules(*nw: NW) -> List[Tuple[bool, C]]:
        pass

    @staticmethod
    @abstractmethod
    def is_unsafe(*nw: NW) -> bool:
        pass


class CountersScWorld(ScWorld[List[NW]]):
    C = List[NW]
    History = List[C]

    def __init__(self, cnt: CountersWorld, max_nw: int, max_depth: int):
        self.cnt = cnt
        self.max_nw = max_nw
        self.max_depth = max_depth

    def ge_max_n(self, nw: NW):
        if isinstance(nw, W):
            return False
        elif isinstance(nw, N):
            return nw.i >= self.max_nw
        else:
            raise ValueError

    def is_too_big(self, c: C) -> bool:
        return any([self.ge_max_n(nw) for nw in c])

    def is_dangerous(self, h: History) -> bool:
        return any([self.is_too_big(c) for c in h]) or len(h) >= self.max_depth

    def is_foldable_to(self, c1: C, c2: C) -> bool:
        return all([nw1.is_in(nw2) for nw1, nw2 in zip(c1, c2)])

    # Driving is deterministic
    def drive(self, c: C) -> List[C]:
        return [r for p, r in self.cnt.rules(*c) if p]

    # Rebuilding is not deterministic,
    # but makes a single configuration from a configuration.

    @staticmethod
    def rebuild1(nw: NW) -> List[NW]:
        if isinstance(nw, W):
            return [W()]
        elif isinstance(nw, N):
            return [nw, W()]
        else:
            raise ValueError

    def rebuild(self, c: C) -> List[C]:
        cs = cartesian([self.rebuild1(nw) for nw in c])
        return [c1 for c1 in cs if not (c1 == c)]

    def develop(self, c: C) -> List[List[C]]:
        return [self.drive(c)] + [[c] for c in self.rebuild(c)]
