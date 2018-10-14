#
# Graphs of configurations
#
# A `Graph` is supposed to represent a residual program.
# Technically, a `Graph` is a tree, with `back` nodes being
# references to parent nodes.
#
# A graph's nodes contain configurations. Here we abstract away
# from the concrete structure of configurations.
# In this model the arrows in the graph carry no information,
# because this information can be kept in nodes.
# (Hence, this information is supposed to be encoded inside
# "configurations".)
#
# To simplify the machinery, back-nodes in this model of
# supercompilation do not contain explicit references
# to parent nodes. Hence, `Back(c)` means that `c` is foldable
# to a parent configuration (perhaps, to several ones).
#
# * Back-nodes are produced by folding a configuration to another
#  configuration in the history.
# * Forth-nodes are produced by
#    + decomposing a configuration into a number of other configurations
#      (e.g. by driving or taking apart a let-expression), or
#    + by rewriting a configuration by another one (e.g. by generalization,
#      introducing a let-expression or applying a lemma during
#      two-level supercompilation).

import itertools
from typing import TypeVar, Generic, List, Optional, Callable, Tuple

from numpy.core import long

C = TypeVar('C')


# Graph

class Graph(Generic[C]):
    def __repr__(self):
        return self.__str__()


class Back(Graph[C]):
    def __init__(self, c: C):
        self.c = c

    def __eq__(self, other):
        return self is other or \
               (type(other) is Back and self.c == other.c)

    def __str__(self):
        return "Back(%s)" % self.c.__str__()


class Forth(Graph[C]):
    def __init__(self, c: C, gs: List[Graph[C]]):
        self.c = c
        self.gs = gs

    def __eq__(self, other):
        return self is other or \
               (type(other) is Forth and
                self.c == other.c and self.gs == other.gs)

    def __str__(self):
        return "Forth(%s, %s)" % (self.c, self.gs)


# Graph pretty printer

def graph_pretty_printer(g: Graph[C], indent="", cstr=str):
    sb = []
    if isinstance(g, Back):
        sb.append(indent + "|__" + cstr(g.c) + "*")
    elif isinstance(g, Forth):
        sb.append(indent + "|__" + cstr(g.c))
        for g in g.gs:
            sb.append("\n  " + indent + "|")
            sb.append("\n" + graph_pretty_printer(g, indent + "  ", cstr))
    else:
        raise ValueError
    return "".join(sb)


#
# Lazy graphs of configurations
#

# A `LazyGraph a` represents a finite set of graphs
# of configurations (whose type is `Graph a`).
#
# "Lazy" graphs of configurations will be produced
# by the "lazy" (staged) version of multi-result
# supercompilation.

# LazyGraph

class LazyGraph(Generic[C]):
    def __repr__(self):
        return self.__str__()


class Empty(LazyGraph[C]):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Empty, cls).__new__(cls)
        return cls.instance


class Stop(LazyGraph[C]):
    def __init__(self, c: C):
        self.c = c

    def __eq__(self, other):
        return self is other or \
               (type(other) is Stop and self.c == other.c)

    def __str__(self):
        return "Stop(%s)" % self.c


class Build(LazyGraph[C]):
    def __init__(self, c: C, lss: List[List[LazyGraph[C]]]):
        self.c = c
        self.lss = lss

    def __eq__(self, other):
        return self is other or \
               (type(other) is Build and
                self.c == other.c and self.lss == other.lss)

    def __str__(self):
        return "Build(%s, %s)" % (self.c, self.lss)


# Lazy coraph

class LazyGraph8(Generic[C]):
    pass


class Empty8(LazyGraph8[C]):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Empty8, cls).__new__(cls)
        return cls.instance


class Stop8(LazyGraph8[C]):
    def __init__(self, c: C):
        self.c = c

    def __str__(self):
        return "Stop8(%s)" % self.c

    def __repr__(self):
        return self.__str__()


class Build8(LazyGraph8[C]):
    def __init__(self, c: C, lss8: Callable[[], List[List[LazyGraph8[C]]]]):
        self.c = c
        self._lss8 = lss8

    @property
    def lss(self) -> List[List[LazyGraph8[C]]]:
        if hasattr(self, '_lss'):
            return self._lss
        else:
            self._lss = self._lss8()
            return self._lss

    def __str__(self):
        return "Build8(%s, %s)" % (self.c, self.lss)

    def __repr__(self):
        return self.__str__()


#
# Cartesian product
#

X = TypeVar('X')


def cartesian(xss: List[List[X]]) -> List[List[X]]:
    return [list(xs) for xs in itertools.product(*xss)]


# The semantics of a `LazyGraph` is formally defined by
# the interpreter `unroll` that generates a sequence of `Graph` from
# the `LazyGraph` by executing commands recorded in the `LazyGraph`.

def unroll(l: LazyGraph[C]) -> List[Graph[C]]:
    if isinstance(l, Empty):
        return []
    elif isinstance(l, Stop):
        return [Back(l.c)]
    elif isinstance(l, Build):
        gss = [gs
               for ls in l.lss
               for gs in cartesian([unroll(l) for l in ls])]
        return [Forth(l.c, gs) for gs in gss]
    else:
        raise ValueError


# Usually, we are not interested in the whole bag `unroll(l)`.
# The goal is to find "the best" or "most interesting" graphs.
# Hence, there should be developed some techniques of extracting
# useful information from a `LazyGraph` without evaluating
# `unroll(l)` directly.

# This can be formulated in the following form.
# Suppose that a function `select` filters bags of graphs,
# removing "bad" graphs, so that
#     select(unroll(l))
# generates the bag of "good" graphs.
# Let us find a function `extract` such that
#     extract(l) == select(unroll(l))
# In many cases, `extract` may be more efficient (by several orders
# of magnitude) than the composition `select . unroll`.
# Sometimes, `extract` can be formulated in terms of "cleaners" of
# lazy graphs. Let `clean` be a function that transforms lazy graphs,
# such that
#     unroll(clean(l)) ⊆ unroll(l)
# Then `extract` can be constructed in the following way:
#     extract(l) == unroll(clean(l))
# Theoretically speaking, `clean` is the result of "promoting" `select`:
#     (select compose unroll)(l) == (unroll compose clean)(l)
# The nice property of cleaners is that they are composable:
# given `clean1` and `clean2`, `clean2 compose clean1` is also a cleaner.

#
# Some filters
#

# Removing graphs that contain "bad" configurations.
# Configurations represent states of a computation process.
# Some of these states may be "bad" with respect to the problem
# that is to be solved by means of supercompilation.

def bad_graph(bad: Callable[[C], bool]) -> Callable[[Graph[C]], bool]:
    def inspect(g: Graph[C]) -> bool:
        if isinstance(g, Back):
            return bad(g.c)
        elif isinstance(g, Forth):
            return bad(g.c) or any(inspect(g1) for g1 in g.gs)
        else:
            raise ValueError

    return inspect


# This filter removes the graphs containing "bad" configurations.

def fl_bad_conf(bad: Callable[[C], bool], gs: List[Graph[C]]) -> List[Graph[C]]:
    return list(filter(bad_graph(bad), gs))


#
# Some cleaners
#

# `cl_empty` removes subtrees that represent empty sets of graphs.

def cl_empty(l: LazyGraph[C]) -> LazyGraph[C]:
    if isinstance(l, Empty):
        return l
    elif isinstance(l, Stop):
        return l
    elif isinstance(l, Build):
        lss1 = cl_empty2(l.lss)
        return Empty() if len(lss1) == 0 else Build(l.c, lss1)
    else:
        raise ValueError


def cl_empty2(lss: List[List[LazyGraph[C]]]) -> List[List[LazyGraph[C]]]:
    return [ls for ls in map(cl_empty1, lss) if not (ls is None)]


def cl_empty1(ls: List[LazyGraph[C]]) -> Optional[List[LazyGraph[C]]]:
    ls1 = [cl_empty(l) for l in ls]
    return None if Empty() in ls1 else ls1


# Removing graphs that contain "bad" configurations.
# The cleaner `cl_bad_conf` corresponds to the filter `fl_bad_conf`.
# `cl_bad_conf` exploits the fact that "badness" is monotonic,
# in the sense that a single "bad" configuration spoils the whole
# graph.

def cl_bad_conf(bad: Callable[[C], bool]) \
        -> Callable[[LazyGraph[C]], LazyGraph[C]]:
    def inspect(l: LazyGraph[C]) -> LazyGraph[C]:
        if isinstance(l, Empty):
            return Empty()
        elif isinstance(l, Stop):
            return Empty() if bad(l.c) else l
        elif isinstance(l, Build):
            return Empty() if bad(l.c) else \
                Build(l.c, [[inspect(l1) for l1 in ls] for ls in l.lss])
        else:
            raise ValueError

    return inspect


#
# The graph returned by `cl_bad_conf` may be cleaned by `cl_empty`.
#

def cl_empty_and_bad(bad: Callable[[C], bool]) \
        -> Callable[[LazyGraph[C]], LazyGraph[C]]:
    def inspect(l: LazyGraph[C]) -> LazyGraph[C]:
        return cl_empty(cl_bad_conf(bad)(l))

    return inspect


#
# Extracting a graph of minimal size (if any).
#

def graph_size(g: Graph[C]) -> long:
    if isinstance(g, Back):
        return 1
    elif isinstance(g, Forth):
        return 1 + sum(map(graph_size, g.gs))
    else:
        raise ValueError


# Now we define a cleaner `cl_min_size` that produces a lazy graph
# representing the smallest graph (or the empty set of graphs).

# We use a trick: ∞ is represented by None in
# (None , None).

def cl_min_size(l: LazyGraph[C]) -> LazyGraph[C]:
    _, l1 = sel_min_size(l)
    return l1


OI = Optional[long]
OILG = Tuple[OI, LazyGraph[C]]
OILLG = Tuple[OI, List[LazyGraph[C]]]


def sel_min_size(l: LazyGraph[C]) -> OILG:
    if isinstance(l, Empty):
        return None, Empty()
    elif isinstance(l, Stop):
        return 1, l
    elif isinstance(l, Build):
        k, ls = sel_min_size2(l.lss)
        if k is None:
            return None, Empty()
        else:
            return 1 + k, Build(l.c, [ls])
    else:
        raise ValueError


def select_min2(kx1: OILLG, kx2: OILLG) -> OILLG:
    k1, _ = kx1
    k2, _ = kx2
    if k2 is None:
        return kx1
    elif k1 is None:
        return kx2
    else:
        return kx1 if k1 <= k2 else kx2


def sel_min_size2(lss: List[List[LazyGraph[C]]]) -> OILLG:
    acc = None, []
    for ls in lss:
        acc = select_min2(sel_min_size_and(ls), acc)
    return acc


def sel_min_size_and(ls: List[LazyGraph[C]]) -> OILLG:
    k = 0
    ls1 = []
    for l in ls:
        k1, l1 = sel_min_size(l)
        k = add_min_size(k, k1)
        ls1.append(l1)
    return k, ls1


def add_min_size(x1: OI, x2: OI) -> OI:
    if x1 is None or x2 is None:
        return None
    else:
        return x1 + x2

#
# `cl_min_size` is sound:
#
#  Let cl_min_size(l) == (k , l'). Then
#     unroll(l') ⊆ unroll(l)
#     k == graph_size ((unroll(l')[0]))
