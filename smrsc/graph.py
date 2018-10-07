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


# Graph

class Graph(object):
    pass


class Back(Graph):
    def __init__(self, c):
        self.c = c

    def __eq__(self, other):
        return self is other or \
               (type(other) is Back and self.c == other.c)

    def __str__(self):
        return "Back(%s)" % self.c.__str__()

    def __repr__(self):
        return self.__str__()


class Forth(Graph):
    def __init__(self, c, gs):
        self.c = c
        self.gs = gs

    def __eq__(self, other):
        return self is other or \
               (type(other) is Forth and
                self.c == other.c and self.gs == other.gs)

    def __str__(self):
        return "Forth(%s, %s)" % (self.c, self.gs)

    def __repr__(self):
        return self.__str__()


# GraphPrettyPrinter

# object GraphPrettyPrinter {
#   def toString(g: Graph[_], indent: String = ""): StringBuilder = {
#     val sb = new StringBuilder()
#     g match {
#       case Back(c) =>
#         sb.append(indent + "|__" + c + "*")
#       case Forth(c, gs) =>
#         sb.append(indent + "|__" + c)
#         for (g <- gs) {
#           sb.append("\n  " + indent + "|")
#           sb.append("\n" + toString(g, indent + "  "))
#         }
#     }
#     sb
#   }
# }

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

class LazyGraph:
    pass


# A singleton?
# class Empty(LazyGraph):
#     def __str__(self):
#         return "Empty()"


class Stop(LazyGraph):
    def __init__(self, c):
        self.c = c

    def __eq__(self, other):
        return self is other or \
               (type(other) is Stop and self.c == other.c)

    def __str__(self):
        return "Stop(%s)" % self.c

    def __repr__(self):
        return self.__str__()


class Build(LazyGraph):
    def __init__(self, c, lss):
        self.c = c
        self.lss = lss

    def __eq__(self, other):
        return self is other or \
               (type(other) is Build and
                self.c == other.c and self.lss == other.lss)

    def __str__(self):
        return "Build(%s, %s)" % (self.c, self.lss)

    def __repr__(self):
        return self.__str__()


# LazyCoraph

# sealed trait LazyCograph[+C]
#
# object LazyCograph {
#
#   case object Empty8
#     extends LazyCograph[Nothing]
#
#   case class Stop8[C](c: C)
#     extends LazyCograph[C]
#
#   private
#   class Build8Imp[C](val c: C, val lss: () => List[List[LazyCograph[C]]])
#     extends LazyCograph[C]
#
#   object Build8 {
#     def apply[C](c: C, lss: => List[List[LazyCograph[C]]]): LazyCograph[C] = {
#       lazy val lssVal = lss
#       new Build8Imp[C](c, () => lssVal)
#     }
#
#     def unapply[C](arg: Build8Imp[C]): Option[(C, List[List[LazyCograph[C]]])] =
#       Some(arg.c, arg.lss())
#   }
#
# }

#
# Cartesian product
#

def cartesian(lss):
    return [list(ls) for ls in itertools.product(*lss)]


# The semantics of a `LazyGraph` is formally defined by
# the interpreter `unroll` that generates a sequence of `Graph` from
# the `LazyGraph` by executing commands recorded in the `LazyGraph`.

def unroll_ls(ls):
    return cartesian(map(unroll, ls))


def unroll(l):
    if l is None:
        return []
    elif isinstance(l, Stop):
        return [Back(l.c)]
    elif isinstance(l, Build):
        gss = itertools.chain.from_iterable(map(unroll_ls, l.lss))
        return [Forth(l.c, gs) for gs in gss]
    else:
        raise ValueError


# Usually, we are not interested in the whole bag `unroll(l)`.
# The goal is to find "the best" or "most interesting" graphs.
# Hence, there should be developed some techniques of extracting
# useful information from a `LazyGraph[C]` without evaluating
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

def bad_graph(bad):
    def inspect(g):
        if isinstance(g, Back):
            return bad(g.c)
        elif isinstance(g, Forth):
            return bad(g.c) or any(inspect(g1) for g1 in g.gs)
        else:
            raise ValueError

    return inspect


# This filter removes the graphs containing "bad" configurations.

def fl_bad_conf(bad, gs):
    return list(filter(bad_graph(bad), gs))


#
# Some cleaners
#

# `cl_empty` removes subtrees that represent empty sets of graphs.

def cl_empty(l):
    if l is None:
        return l
    elif isinstance(l, Stop):
        return l
    elif isinstance(l, Build):
        lss1 = cl_empty2(l.lss)
        return None if len(lss1) == 0 else Build(l.c, lss1)
    else:
        raise ValueError


def cl_empty2(lss):
    return [ls for ls in map(cl_empty1, lss) if not (ls is None)]


def cl_empty1(ls):
    ls1 = [cl_empty(l) for l in ls]
    return None if None in ls1 else ls1


# Removing graphs that contain "bad" configurations.
# The cleaner `cl_bad_conf` corresponds to the filter `fl_bad_conf`.
# `cl_bad_conf` exploits the fact that "badness" is monotonic,
# in the sense that a single "bad" configuration spoils the whole
# graph.

def cl_bad_conf(bad):
    def inspect(l):
        if l is None:
            return None
        elif isinstance(l, Stop):
            return None if bad(l.c) else l
        elif isinstance(l, Build):
            return None if bad(l.c) else \
                Build(l.c, [[inspect(l1) for l1 in ls] for ls in l.lss])
        else:
            raise ValueError

    return inspect


#
# The graph returned by `cl_bad_conf` may be cleaned by `cl_empty`.
#

def cl_empty_and_bad(bad):
    def inspect(l):
        return cl_empty(cl_bad_conf(bad)(l))

    return inspect


#
# Extracting a graph of minimal size (if any).
#

def graph_size(g):
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

def cl_min_size(l):
    _, l1 = sel_min_size(l)
    return l1


def sel_min_size(l):
    if l is None:
        return None, None
    elif isinstance(l, Stop):
        return 1, l
    elif isinstance(l, Build):
        k, ls = sel_min_size2(l.lss)
        if k is None:
            return None, None
        else:
            return 1 + k, Build(l.c, [ls])
    else:
        raise ValueError


def select_min2(kx1, kx2):
    k1, _ = kx1
    k2, _ = kx2
    if k2 is None:
        return kx1
    elif k1 is None:
        return kx2
    else:
        return kx1 if k1 <= k2 else kx2


def sel_min_size2(lss):
    acc = None, None
    for ls in lss:
        acc = select_min2(sel_min_size_and(ls), acc)
    return acc


def sel_min_size_and(ls):
    k = 0
    ls1 = []
    for l in ls:
        k1, l1 = sel_min_size(l)
        k = add_min_size(k, k1)
        ls1.append(l1)
    return k, ls1


def add_min_size(x1, x2):
    if x1 is None or x2 is None:
        return None
    else:
        return x1 + x2
