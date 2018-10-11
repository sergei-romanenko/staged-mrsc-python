# ### Schemes of different types of big-step supercompilation
#
# A variation of the scheme presented in the paper
#
# Ilya G. Klyuchnikov, Sergei A. Romanenko. Formalizing and Implementing
# Multi-Result Supercompilation.
# In Third International Valentin Turchin Workshop on Metacomputation
# (Proceedings of the Third International Valentin Turchin Workshop on
# Metacomputation. Pereslavl-Zalessky, Russia, July 5-9, 2012).
# A.V. Klimov and S.A. Romanenko, Ed. - Pereslavl-Zalessky: Ailamazyan
# University of Pereslavl, 2012, 260 p. ISBN 978-5-901795-28-6, pages
# 142-164.
#
# Now we formulate an idealized model of big-step multi-result
# supercompilation.
#
# The knowledge about the input language a supercompiler deals with
# is represented by a "world of supercompilation", which is a trait
# that specifies the following.
#
# * `C` is the type of "configurations". Note that configurations are
#   not required to be just expressions with free variables! In general,
#   they may represent sets of states in any form/language and as well may
#   contain any _additional_ information.
#
# * `is_foldable_to` is a "foldability relation". is_foldable_to(c, c') means
#   that c is foldable to c'.
#   (In such cases c' is usually said to be " more general than c".)
#
# * `develop` is a function that gives a number of possible decompositions of
#   a configuration. Let `c` be a configuration and `cs` a list of
#   configurations such that `cs ∈ develop(c)`. Then `c` can be "reduced to"
#   (or "decomposed into") configurations in `cs`.
#
#   Suppose that driving is determinstic and, given a configuration `c`,
#   produces a list of configurations `drive(c)`. Suppose that rebuilding
#   (generalization, application of lemmas) is non-deterministic and
#   `rebuild(c)` is the list of configurations that can be produced by
#   rebuilding. Then (in this special case) `develop` is implemented
#   as follows:
#
#       develop(c) = [drive(c)] + map(lambda cs: [cs] , rebuild(c))
#
# * `History` is a list of configuration that have been produced
#   in order to reach the current configuration.
#
# * `is_dangerous` is a "whistle" that is used to ensure termination of
#   supercompilation. `is_dangerous(h)` means that the history has become
#   "too large".
#
# * `is_foldable_to_history(c, h)` means that `c` is foldable to a configuration
#   in the history `h`.

import itertools
from abc import abstractmethod
from typing import Generic, List

from smrsc.graph import \
    C, cartesian, Graph, Back, Forth, LazyGraph, Empty, Stop, Build


class ScWorld(Generic[C]):
    History = List[C]

    @abstractmethod
    def is_dangerous(self, h: History) -> bool:
        pass

    @abstractmethod
    def is_foldable_to(self, c1: C, c2: C) -> bool:
        pass

    @abstractmethod
    def develop(self, c: C) -> List[List[C]]:
        pass

    def is_foldable_to_history(self, c: C, h: History) -> bool:
        return any(map(lambda c1: self.is_foldable_to(c, c1), h))


# Big-step multi-result supercompilation
# (The naive version builds Cartesian products immediately.)

def naive_mrsc(w: ScWorld[C], c0: C) -> List[Graph[C]]:
    def naive_mrsc_loop(h: w.History, c: C) -> List[Graph[C]]:
        if w.is_foldable_to_history(c, h):
            return [Back(c)]
        elif w.is_dangerous(h):
            return []
        else:
            css = w.develop(c)
            gsss = [cartesian([naive_mrsc_loop([c] + h, c1) for c1 in cs])
                    for cs in css]
            return [Forth(c, gs) for gs in itertools.chain(*gsss)]

    return naive_mrsc_loop([], c0)


# "Lazy" multi-result supercompilation.
# (Cartesian products are not immediately built.)
#
# lazy_mrsc is essentially a "staged" version of naive_mrsc
# with `unroll` being an "interpreter" that evaluates the "program"
# returned by lazy_mrsc.


def lazy_mrsc(w: ScWorld[C], c0: C) -> LazyGraph[C]:
    def lazy_mrsc_loop(h: w.History, c: C) -> LazyGraph[C]:
        if w.is_foldable_to_history(c, h):
            return Stop(c)
        elif w.is_dangerous(h):
            return Empty()
        else:
            css = w.develop(c)
            lss = [[lazy_mrsc_loop([c] + h, c1) for c1 in cs]
                   for cs in css]
            return Build(c, lss)

    return lazy_mrsc_loop([], c0)
