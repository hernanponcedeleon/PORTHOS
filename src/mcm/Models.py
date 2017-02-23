from SC import *
from TSO import *
from PSO import *
from RMO import *
from Alpha import *
from Power import *
from Dead import *

def PowerSC(m, dead=False, write=False):

    s = Solver()
    s.add(PowerConsistent(m))
    s.add(ScInconsistent(m))
    if dead:
        s.add(Dead(m))

    res = s.check()

    return res

def PowerTSO(m, dead=False, write=False):

    s = Solver()
    s.add(PowerConsistent(m))
    s.add(TsoInconsistent(m))
    if dead:
        s.add(Dead(m))

    res = s.check()

    return res


def PowerPSO(m, dead=False, write=False):

    s = Solver()
    s.add(PowerConsistent(m))
    s.add(PsoInconsistent(m))
    if dead:
        s.add(Dead(m))

    res = s.check()

    return res


def PowerRMO(m, dead=False, write=False):

    s = Solver()
    s.add(PowerConsistent(m))
    s.add(RmoInconsistent(m))
    if dead:
        s.add(Dead(m))

    res = s.check()

    return res


def PowerAlpha(m, dead=False, write=False):

    s = Solver()
    s.add(PowerConsistent(m))
    s.add(AlphaInconsistent(m))
    if dead:
        s.add(Dead(m))

    res = s.check()

    return res


def PowerCAV(m, dead=False, write=False):

    s = Solver()
    s.add(PowerConsistent(m))
    s.add(CavInconsistent(m))
    if dead:
        s.add(Dead(m))

    res = s.check()

    return res


def CAVPower(m, dead=False, write=False):

    s = Solver()
    s.add(CavConsistent(m))
    s.add(PowerInconsistent(m))
    if dead:
        s.add(Dead(m))

    res = s.check()

    return res


def AlphaSC(m, dead=False, write=False):

    s = Solver()
    s.add(AlphaConsistent(m))
    s.add(ScInconsistent(m))
    if dead:
        s.add(Dead(m))

    res = s.check()

    return res


def AlphaTSO(m, dead=False, write=False):

    s = Solver()
    s.add(AlphaConsistent(m))
    s.add(TsoInconsistent(m))
    if dead:
        s.add(Dead(m))

    res = s.check()

    return res


def AlphaPSO(m, dead=False, write=False):

    s = Solver()
    s.add(AlphaConsistent(m))
    s.add(PsoInconsistent(m))
    if dead:
        s.add(Dead(m))

    res = s.check()

    return res


def AlphaRMO(m, dead=False, write=False):

    s = Solver()
    s.add(AlphaConsistent(m))
    s.add(RmoInconsistent(m))
    if dead:
        s.add(Dead(m))

    res = s.check()

    return res


def RMOSC(m, dead=False, write=False):

    s = Solver()
    s.add(RmoConsistent(m))
    s.add(ScInconsistent(m))
    if dead:
        s.add(Dead(m))

    res = s.check()

    return res


def RMOTSO(m, dead=False, write=False):

    s = Solver()
    s.add(RmoConsistent(m))
    s.add(TsoInconsistent(m))
    if dead:
        s.add(Dead(m))

    res = s.check()

    return res


def RMOPSO(m, dead=False, write=False):

    s = Solver()
    s.add(RmoConsistent(m))
    s.add(PsoInconsistent(m))
    if dead:
        s.add(Dead(m))

    res = s.check()

    return res


def RMOAlpha(m, dead=False, write=False):

    s = Solver()
    s.add(RmoConsistent(m))
    s.add(AlphaInconsistent(m))
    if dead:
        s.add(Dead(m))

    res = s.check()

    return res


def PSOSC(m, dead=False, write=False):

    s = Solver()
    s.add(PsoConsistent(m))
    s.add(ScInconsistent(m))
    if dead:
        s.add(Dead(m))

    res = s.check()

    return res


def PSOTSO(m, dead=False, write=False):

    s = Solver()
    s.add(PsoConsistent(m))
    s.add(TsoInconsistent(m))
    if dead:
        s.add(Dead(m))

    res = s.check()

    return res


def TSOSC(m, dead=False, write=False):

    s = Solver()
    s.add(TsoConsistent(m))
    s.add(ScInconsistent(m))
    if dead:
        s.add(Dead(m))

    res = s.check()

    return res
