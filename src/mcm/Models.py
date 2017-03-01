from SC import *
from TSO import *
from PSO import *
from RMO import *
from Alpha import *
from Power import *
from Dead import *
from CAV10 import *

def PowerSC(m, dead=False, write=False):

    s = Solver()
    s.add(PowerConsistent(m))
    s.add(ScInconsistent(m))
    if dead:
        s.add(Dead(m))

    res = s.check()

    return (res, s.model() if res == sat else None)

def PowerTSO(m, dead=False, write=False):

    s = Solver()
    s.add(PowerConsistent(m))
    s.add(TsoInconsistent(m))
    if dead:
        s.add(Dead(m))

    res = s.check()

    return (res, s.model() if res == sat else None)


def PowerPSO(m, dead=False, write=False):

    s = Solver()
    s.add(PowerConsistent(m))
    s.add(PsoInconsistent(m))
    if dead:
        s.add(Dead(m))

    res = s.check()

    return (res, s.model() if res == sat else None)


def PowerRMO(m, dead=False, write=False):

    s = Solver()
    s.add(PowerConsistent(m))
    s.add(RmoInconsistent(m))
    if dead:
        s.add(Dead(m))

    res = s.check()

    return (res, s.model() if res == sat else None)


def PowerAlpha(m, dead=False, write=False):

    s = Solver()
    s.add(PowerConsistent(m))
    s.add(AlphaInconsistent(m))
    if dead:
        s.add(Dead(m))

    res = s.check()

    return (res, s.model() if res == sat else None)


def PowerCAV(m, dead=False, write=False):

    s = Solver()
    s.add(PowerConsistent(m))
    s.add(CavInconsistent(m))
    if dead:
        s.add(Dead(m))

    res = s.check()

    return (res, s.model() if res == sat else None)


def CAVPower(m, dead=False, write=False):

    s = Solver()
    s.add(CavConsistent(m))
    s.add(PowerInconsistent(m))
    if dead:
        s.add(Dead(m))

    res = s.check()

    return (res, s.model() if res == sat else None)


def AlphaSC(m, dead=False, write=False):

    s = Solver()
    s.add(AlphaConsistent(m))
    s.add(ScInconsistent(m))
    if dead:
        s.add(Dead(m))

    res = s.check()

    return (res, s.model() if res == sat else None)


def AlphaTSO(m, dead=False, write=False):

    s = Solver()
    s.add(AlphaConsistent(m))
    s.add(TsoInconsistent(m))
    if dead:
        s.add(Dead(m))

    res = s.check()

    return (res, s.model() if res == sat else None)


def AlphaPSO(m, dead=False, write=False):

    s = Solver()
    s.add(AlphaConsistent(m))
    s.add(PsoInconsistent(m))
    if dead:
        s.add(Dead(m))

    res = s.check()

    return (res, s.model() if res == sat else None)


def AlphaRMO(m, dead=False, write=False):

    s = Solver()
    s.add(AlphaConsistent(m))
    s.add(RmoInconsistent(m))
    if dead:
        s.add(Dead(m))

    res = s.check()

    return (res, s.model() if res == sat else None)


def RMOSC(m, dead=False, write=False):

    s = Solver()
    s.add(RmoConsistent(m))
    s.add(ScInconsistent(m))
    if dead:
        s.add(Dead(m))

    res = s.check()

    return (res, s.model() if res == sat else None)


def RMOTSO(m, dead=False, write=False):

    s = Solver()
    s.add(RmoConsistent(m))
    s.add(TsoInconsistent(m))
    if dead:
        s.add(Dead(m))

    res = s.check()

    return (res, s.model() if res == sat else None)


def RMOPSO(m, dead=False, write=False):

    s = Solver()
    s.add(RmoConsistent(m))
    s.add(PsoInconsistent(m))
    if dead:
        s.add(Dead(m))

    res = s.check()

    return (res, s.model() if res == sat else None)


def RMOAlpha(m, dead=False, write=False):

    s = Solver()
    s.add(RmoConsistent(m))
    s.add(AlphaInconsistent(m))
    if dead:
        s.add(Dead(m))

    res = s.check()

    return (res, s.model() if res == sat else None)


def PSOSC(m, dead=False, write=False):

    s = Solver()
    s.add(PsoConsistent(m))
    s.add(ScInconsistent(m))
    if dead:
        s.add(Dead(m))

    res = s.check()

    return (res, s.model() if res == sat else None)


def PSOTSO(m, dead=False, write=False):

    s = Solver()
    s.add(PsoConsistent(m))
    s.add(TsoInconsistent(m))
    if dead:
        s.add(Dead(m))

    res = s.check()

    return (res, s.model() if res == sat else None)


def TSOSC(m, dead=False, write=False):

    s = Solver()
    s.add(TsoConsistent(m))
    s.add(ScInconsistent(m))
    if dead:
        s.add(Dead(m))

    res = s.check()

    return (res, s.model() if res == sat else None)
