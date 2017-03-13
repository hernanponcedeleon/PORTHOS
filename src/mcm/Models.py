import sys
from SC import *
from TSO import *
from PSO import *
from RMO import *
from Alpha import *
from Power import *
from Dead import *
from CAV10 import *

class bcolors:
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def portability(m, source, target, dead=False):
    s = Solver()

    s.add(encodeDomain(m))
    s.add(encode(m))

    if source == "sc":
        s.add(Sc(m))
        s.add(ScInconsistent(m))
    elif source == "tso":
        s.add(Tso(m))
        s.add(TsoInconsistent(m))
    elif source == "pso":
        s.add(Pso(m))
        s.add(PsoInconsistent(m))
    elif source == "rmo":
        s.add(Rmo(m))
        s.add(RmoInconsistent(m))
    elif source == "alpha":
        s.add(Alpha(m))
        s.add(AlphaInconsistent(m))
    elif source == "power":
        s.add(Power(m))
        s.add(PowerInconsistent(m))
    elif source == "cav10":
        s.add(Cav(m))
        s.add(CavInconsistent(m))
    else:
        print bcolors.FAIL + 'The source model is not supported.' + bcolors.ENDC
        sys.exit()

    if target == "sc":
        s.add(Sc(m))
        s.add(ScConsistent(m))
    elif target == "tso":
        s.add(Tso(m))
        s.add(TsoConsistent(m))
    elif target == "pso":
        s.add(Pso(m))
        s.add(PsoConsistent(m))
    elif target == "rmo":
        s.add(Rmo(m))
        s.add(RmoConsistent(m))
    elif target == "alpha":
        s.add(Alpha(m))
        s.add(AlphaConsistent(m))
    elif target == "power":
        s.add(Power(m))
        s.add(PowerConsistent(m))
    elif target == "cav10":
        s.add(Cav(m))
        s.add(CavConsistent(m))
    else:
        print bcolors.FAIL + 'The target model is not supported.' + bcolors.ENDC
        sys.exit()

    if dead:
        s.add(Dead(m))

    res = s.check()

    return (res, s.model() if res == sat else None)
