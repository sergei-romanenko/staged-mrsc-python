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


class MSI(CountersWorld):
    C = List[Union[NW, int]]

    @staticmethod
    def start() -> C:
        return [w, 0, 0]

    @staticmethod
    def rules(i: NW, m: NW, s: NW) -> List[Tuple[bool, C]]:
        return [
            (i >= 1, [i + m + s - 1, 1, 0]),
            (s >= 1, [i + m + s - 1, 1, 0]),
            (i >= 1, [i - 1, 0, m + s + 1])]

    @staticmethod
    def is_unsafe(i: NW, m: NW, s: NW) -> bool:
        return (m >= 1 and s >= 1) or (m >= 2)


class MOSI(CountersWorld):
    C = List[Union[NW, int]]

    @staticmethod
    def start() -> C:
        return [w, 0, 0, 0]

    @staticmethod
    def rules(i: NW, o: NW, s: NW, m: NW) -> List[Tuple[bool, C]]:
        return [
            (i >= 1, [i - 1, m + o, s + 1, 0]),
            (o >= 1, [i + o + s + m - 1, 0, 0, 1]),
            # wI
            (i >= 1, [i + o + s + m - 1, 0, 0, 1]),
            # wS
            (s >= 1, [i + o + s + m - 1, 0, 0, 1]),
            # se
            (s >= 1, [i + 1, o, s - 1, m]),
            # wbm
            (m >= 1, [i + 1, o, s, m - 1]),
            # wbo
            (o >= 1, [i + 1, o - 1, s, m])]

    @staticmethod
    def is_unsafe(i: NW, o: NW, s: NW, m: NW) -> bool:
        return (o >= 2) or (m >= 2) or (s >= 1 and m >= 1)


class ReaderWriter(CountersWorld):
    C = List[Union[NW, int]]

    @staticmethod
    def start() -> C:
        return [1, 0, 0, w, 0, 0]

    @staticmethod
    def rules(x2: NW, x3: NW, x4: NW, x5: NW, x6: NW, x7: NW) \
            -> List[Tuple[bool, C]]:
        return [
            # r1
            (x2 >= 1 and x4.is_eq(0) and x7 >= 1,
             [x2 - 1, x3 + 1, 0, x5, x6, x7]),
            # r2
            (x2 >= 1 and x6 >= 1,
             [x2, x3, x4 + 1, x5, x6 - 1, x7]),
            # r3
            (x3 >= 1,
             [x2 + 1, x3 - 1, x4, x5 + 1, x6, x7]),
            # r4
            (x4 >= 1,
             [x2, x3, x4 - 1, x5 + 1, x6, x7]),
            # r5
            (x5 >= 1,
             [x2, x3, x4, x5 - 1, x6 + 1, x7]),
            # r6
            (x5 >= 1,
             [x2, x3, x4, x5 - 1, x6, x7 + 1])]

    @staticmethod
    def is_unsafe(x2: NW, x3: NW, x4: NW, x5: NW, x6: NW, x7: NW) -> bool:
        return x3 >= 1 and x4 >= 1


class MESI(CountersWorld):
    C = List[Union[NW, int]]

    @staticmethod
    def start() -> C:
        return [w, 0, 0, 0]

    @staticmethod
    def rules(i: NW, e: NW, s: NW, m: NW) -> List[Tuple[bool, C]]:
        return [
            (i >= 1, [i - 1, 0, s + e + m + 1, 0]),
            (e >= 1, [i, e - 1, s, m + 1]),
            (s >= 1, [i + e + s + m - 1, 1, 0, 0]),
            (i >= 1, [i + e + s + m - 1, 1, 0, 0])]

    @staticmethod
    def is_unsafe(i: NW, e: NW, s: NW, m: NW) -> bool:
        return m >= 2 or (s >= 1 and m >= 1)


class MOESI(CountersWorld):
    C = List[Union[NW, int]]

    @staticmethod
    def start() -> C:
        return [w, 0, 0, 0, 0]

    @staticmethod
    def rules(i: NW, m: NW, s: NW, e: NW, o: NW) -> List[Tuple[bool, C]]:
        return [
            # rm
            (i >= 1, [i - 1, 0, s + e + 1, 0, o + m]),
            # wh2
            (e >= 1, [i, m + 1, s, e - 1, o]),
            # wh3
            (s + o >= 1, [i + m + s + e + o - 1, 0, 0, 1, 0]),
            # wm
            (i >= 1, [i + m + s + e + o - 1, 0, 0, 1, 0])
        ]

    @staticmethod
    def is_unsafe(i: NW, m: NW, s: NW, e: NW, o: NW) -> bool:
        return (m >= 1 and (e + s + o) >= 1) or (m >= 2) or (e >= 2)


class Illinois(CountersWorld):
    C = List[Union[NW, int]]

    @staticmethod
    def start() -> C:
        return [w, 0, 0, 0]

    @staticmethod
    def rules(i: NW, e: NW, d: NW, s: NW) -> List[Tuple[bool, C]]:
        return [
            # r2
            (i >= 1 and e.is_eq(0) and d.is_eq(0) and s.is_eq(0),
             [i - 1, 1, 0, 0]),
            # r3
            (i >= 1 and d >= 1,
             [i - 1, e, d - 1, s + 2]),
            # r4
            (i >= 1 and s + e >= 1,
             [i - 1, 0, d, s + e + 1]),
            # r6
            (e >= 1,
             [i, e - 1, d + 1, s]),
            # r7
            (s >= 1,
             [i + s - 1, e, d + 1, 0]),
            # r8
            (i >= 1,
             [i + e + d + s - 1, 0, 1, 0]),
            # r9
            (d >= 1,
             [i + 1, e, d - 1, s]),
            # r10
            (s >= 1,
             [i + 1, e, d, s - 1]),
            # r11
            (e >= 1,
             [i + 1, e - 1, d, s])]

    @staticmethod
    def is_unsafe(i: NW, e: NW, d: NW, s: NW) -> bool:
        return (d >= 1 and s >= 1) or (d >= 2)


class Berkley(CountersWorld):
    C = List[Union[NW, int]]

    @staticmethod
    def start() -> C:
        return [w, 0, 0, 0]

    @staticmethod
    def rules(i: NW, n: NW, u: NW, e: NW) -> List[Tuple[bool, C]]:
        return [
            # rm
            (i >= 1, [i - 1, n + e, u + 1, 0]),
            # wm
            (i >= 1, [i + n + u + e - 1, 0, 0, 1]),
            # wh1
            (n + u >= 1, [i + n + u - 1, 0, 0, e + 1])]

    @staticmethod
    def is_unsafe(i: NW, n: NW, u: NW, e: NW) -> bool:
        return (e >= 1 and u + n >= 1) or (e >= 2)


class Firefly(CountersWorld):
    C = List[Union[NW, int]]

    @staticmethod
    def start() -> C:
        return [w, 0, 0, 0]

    @staticmethod
    def rules(i: NW, e: NW, s: NW, d: NW) -> List[Tuple[bool, C]]:
        return [
            # rm1
            (i >= 1 and d.is_eq(0) and s.is_eq(0) and e.is_eq(0),
             [i - 1, 1, 0, 0]),
            # rm2
            (i >= 1 and d >= 1,
             [i - 1, e, s + 2, d - 1]),
            # rm3
            (i >= 1 and s + e >= 1,
             [i - 1, 0, s + e + 1, d]),
            # wh2
            (e >= 1,
             [i, e - 1, s, d + 1]),
            # wh3
            (s.is_eq(1),
             [i, e + 1, 0, d]),
            # wm
            (i >= 1,
             [i + e + d + s - 1, 0, 0, 1])]

    @staticmethod
    def is_unsafe(i: NW, e: NW, s: NW, d: NW) -> bool:
        return (d >= 1 and s + e >= 1) or (e >= 2) or (d >= 2)


class Futurebus(CountersWorld):
    C = List[Union[NW, int]]

    @staticmethod
    def start() -> C:
        return [w, 0, 0, 0, 0, 0, 0, 0, 0]

    @staticmethod
    def rules(i: NW, sU: NW, eU: NW, eM: NW, pR: NW,
              pW: NW, pEMR: NW, pEMW: NW, pSU: NW) -> List[Tuple[bool, C]]:
        return [
            # r2
            (i >= 1 and pW.is_eq(0),
             [i - 1, 0, 0, 0, pR + 1, pW, pEMR + eM, pEMW, pSU + sU + eU]),
            # r3
            (pEMR >= 1,
             [i, sU + pR + 1, eU, eM, 0, pW, pEMR - 1, pEMW, pSU]),
            # r4
            (pSU >= 1,
             [i, sU + pR + pSU, eU, eM, 0, pW, pEMR, pEMW, 0]),
            # r5
            (pR >= 2 and pSU.is_eq(0) and pEMR.is_eq(0),
             [i, sU + pR, eU, eM, 0, pW, 0, pEMW, 0]),
            # r6
            (pR.is_eq(1) and pSU.is_eq(0) and pEMR.is_eq(0),
             [i, sU, eU + 1, eM, 0, pW, 0, pEMW, 0]),
            # wm1
            (i >= 1 & pW.is_eq(0),
             [i + eU + sU + pSU + pR + pEMR - 1, 0, 0, 0, 0, 1, 0, pEMW + eM, 0]),
            # wm2
            (pEMW >= 1,
             [i + 1, sU, eU, eM + pW, pR, 0, pEMR, pEMW - 1, pSU]),
            # wm3
            (pEMW.is_eq(0),
             [i, sU, eU, eM + pW, pR, 0, pEMR, 0, pSU]),
            # wh2
            (eU >= 1,
             [i, sU, eU - 1, eM + 1, pR, pW, pEMR, pEMW, pSU]),
            # wh2
            (sU >= 1,
             [i + sU - 1, 0, eU, eM + 1, pR, pW, pEMR, pEMW, pSU])]

    @staticmethod
    def is_unsafe(i: NW, sU: NW, eU: NW, eM: NW, pR: NW,
                  pW: NW, pEMR: NW, pEMW: NW, pSU: NW) -> bool:
        return (sU >= 1 and eU + eM >= 1) or \
               (eU + eM >= 2) or \
               (pR >= 1 and pW >= 1) or \
               (pW >= 2)


class Xerox(CountersWorld):
    C = List[Union[NW, int]]

    @staticmethod
    def start() -> C:
        return [w, 0, 0, 0, 0]

    @staticmethod
    def rules(i: NW, sc: NW, sd: NW, d: NW, e: NW) -> List[Tuple[bool, C]]:
        return [
            # (1) rm1
            (i >= 1 and d.is_eq(0) and sc.is_eq(0) and sd.is_eq(0) and e.is_eq(0),
             [i - 1, 0, 0, 0, 1]),
            # (2) rm2
            (i >= 1 and d + sc + e + sd >= 1,
             [i - 1, sc + e + 1, sd + d, 0, 0]),
            # (3) wm1
            (i >= 1 and d.is_eq(0) and sc.is_eq(0) and sd.is_eq(0) and e.is_eq(0),
             [i - 1, 0, 0, 1, 0]),
            # (4) wm2
            (i >= 1 and d + sc + e + sd >= 1,
             [i - 1, sc + e + 1 + (sd + d), sd, 0, 0]),
            # (5) wh1
            (d >= 1,
             [i + 1, sc, sd, d - 1, e]),
            # (6) wh2
            (sc >= 1,
             [i + 1, sc - 1, sd, d, e]),
            # (7) wh3
            (sd >= 1,
             [i + 1, sc, sd - 1, d, e]),
            # (8) wh4
            (e >= 1,
             [i + 1, sc, sd, d, e - 1])
        ]

    @staticmethod
    def is_unsafe(i: NW, sc: NW, sd: NW, d: NW, e: NW) -> bool:
        return (d >= 1 and (e + sc + sd) >= 1) or \
               (e >= 1 and (sc + sd) >= 1) or \
               (d >= 2) or \
               (e >= 2)


class DataRace(CountersWorld):
    C = List[Union[NW, int]]

    @staticmethod
    def start() -> C:
        return [w, 0, 0]

    @staticmethod
    def rules(out: NW, cs: NW, scs: NW) -> List[Tuple[bool, C]]:
        return [
            # 1
            (out >= 1 and cs.is_eq(0) and scs.is_eq(0),
             [out - 1, 1, 0]),
            # 2
            (out >= 1 and cs.is_eq(0),
             [out - 1, 0, scs + 1]),
            # 3
            (cs >= 1,
             [out + 1, cs - 1, scs]),
            # 4
            (scs >= 1,
             [out + 1, cs, scs - 1])]

    @staticmethod
    def is_unsafe(out: NW, cs: NW, scs: NW) -> bool:
        return cs >= 1 and scs >= 1
