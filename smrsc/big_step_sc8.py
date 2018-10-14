#
# Infinite trees/graphs
#

#
# Lazy cographs of configurations
#

# A `LazyGraph8[C]` represents a (potentially) infinite set of graphs
# of configurations (whose type is `Graph[C]`).
#
# "Lazy" cographs of configurations will be produced
# by the "lazy" (staged) version of multi-result
# supercompilation.

from smrsc.graph import *
from smrsc.big_step_sc import ScWorld


# build_cograph

def build_cograph(w: ScWorld[C], c0: C) -> LazyGraph8[C]:
    def build_cograph_loop(h: w.History, c: C) -> LazyGraph8[C]:
        if w.is_foldable_to_history(c, h):
            return Stop8(c)
        else:
            def lss():
                return [[build_cograph_loop([c] + h, c1) for c1 in cs]
                        for cs in w.develop(c)]

            return Build8(c, lss)

    return build_cograph_loop([], c0)


# prune_cograph

def prune_cograph(w: ScWorld[C], l0: LazyGraph8[C]) -> LazyGraph[C]:
    def prune_cograph_loop(h: w.History, l: LazyGraph8[C]) -> LazyGraph[C]:
        if isinstance(l, Empty8):
            return Empty()
        elif isinstance(l, Stop8):
            return Stop(l.c)
        elif isinstance(l, Build8):
            if w.is_dangerous(h):
                return Empty()
            else:
                lss = [[prune_cograph_loop([l.c] + h, l1) for l1 in ls]
                       for ls in l.lss]
                return Build(l.c, lss)
        else:
            raise ValueError

    return prune_cograph_loop([], l0)


#
# Now that we have docomposed `lazy_mrsc`
#     lazy_mrsc ≗ prune_cograph ∘ build_cograph
# we can push some cleaners over `prune_cograph`.
#
# Suppose `clean∞` is a cograph cleaner such that
#     clean ∘ prune_cograph ≗ prune_cograph ∘ clean∞
# then
#     clean ∘ lazy_mrsc ≗
#       clean ∘ (prune_cograph ∘ build_cograph) ≗
#       (prune_cograph ∘ clean∞) ∘ build_cograph
#       prune_cograph ∘ (clean∞ ∘ build_cograph)
#
# The good thing is that `build_cograph` and `clean∞` work in a lazy way,
# generating subtrees by demand. Hence, evaluating
#     unroll( prune-cograph ∘ (clean∞ (build-cograph c)) )
# may be less time and space consuming than evaluating
#     unroll( clean (lazy-mrsc c) )
#

def cl8_bad_conf(bad: Callable[[C], bool]) \
        -> Callable[[LazyGraph8[C]], LazyGraph8[C]]:
    def inspect(l: LazyGraph8[C]) -> LazyGraph8[C]:
        if isinstance(l, Empty8):
            return Empty8()
        elif isinstance(l, Stop8):
            return Empty8() if bad(l.c) else l
        elif isinstance(l, Build8):
            if bad(l.c):
                return Empty8()
            else:
                def lss():
                    return [[inspect(l1) for l1 in ls] for ls in l.lss]

                return Build8(l.c, lss)
        else:
            raise ValueError

    return inspect


#
# A cograph can be cleaned to remove some empty alternatives.
#
# Note that the cleaning is not perfect, because `cl8_empty` has to pass
# the productivity check.
# So, `build(c, [])` is not (recursively) replaced with `Empty8()`. as is done
# by `cl_empty`.
#


def cl8_empty(l: LazyGraph8[C]) -> LazyGraph8[C]:
    if isinstance(l, Empty8):
        return l
    elif isinstance(l, Stop8):
        return l
    elif isinstance(l, Build8):
        def lss():
            lss1 = [[cl8_empty(l1) for l1 in ls] for ls in l.lss]
            return [ls for ls in lss1 if not (Empty8() in ls)]

        return Build8(l.c, lss)
    else:
        raise ValueError


# An optimized version of `prune_cograph`.
# The difference is that empty subtrees are removed
# "on the fly".

def prune(w: ScWorld[C], l0: LazyGraph8[C]) -> LazyGraph[C]:
    def prune_loop(h: w.History, l: LazyGraph8[C]) -> LazyGraph[C]:
        if isinstance(l, Empty8):
            return Empty()
        elif isinstance(l, Stop8):
            return Stop(l.c)
        elif isinstance(l, Build8):
            if w.is_dangerous(h):
                return Empty()
            else:
                lss1 = [ls for ls in l.lss if not (Empty8() in ls)]
                lss2 = [[prune_loop([l.c] + h, l1) for l1 in ls]
                        for ls in lss1]
                return Build(l.c, lss2)
        else:
            raise ValueError

    return prune_loop([], l0)
