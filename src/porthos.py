#!/Users/ponceh1/Documents/tools/pypy2-v5.3.0-osx64/bin/pypy

import sys, getopt
sys.path.append('./mcm/')
sys.path.append('./program/')
sys.path.append('./parsers/')
sys.path.append('./encodings/')
from ParserPorthos import *
from ParserAssembly import *
from Models import *
from z3 import *

def main(argv):

    inputfile = None
    source = None
    target = None
    dead = False
    verbose = False
    try:
        opts, args = getopt.getopt(argv,"i:s:t:dv")
    except getopt.GetoptError:
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-i":
            inputfile = arg
	elif opt == "-s":
            source = arg
        elif opt == "-t":
            target = arg
        elif opt == "-d":
            dead = True
        elif opt == "-v":
            verbose = True
    if inputfile == None:
	raise Exception("No input file loaded")
    if not (source in ["sc", "tso", "pso", "rmo", "alpha", "power", "cav10"]):
        raise Exception('Source model is not valid. Select between sc, tso, pso, rmo, alpha, power, cav10')
    if not (target in ["tso", "pso", "rmo", "alpha", "power", "cav10"]):
        raise Exception('Target model is not valid. Select between tso, pso, rmo, alpha, power, cav10')

    if inputfile.endswith('.litmus'):
        program = parseLitmus(inputfile)
    elif inputfile.endswith('.pts'):
        program = parsePorthosFile(inputfile)
    else:
        raise Exception('Input is not a .litmus or .pts file')

    if verbose:
        print program

    program.initialize()

    print "Checking portability between %s and %s" %(source,target)

    if source == "sc" and target == "tso":
        sol = TSOSC(program, dead)
    elif source == "sc" and target == "pso":
        sol = PSOSC(program, dead)
    elif source == "sc" and target == "rmo":
        sol = RMOSC(program, dead)
    elif source == "sc" and target == "alpha":
        sol = AlphaSC(program, dead)
    elif source == "sc" and target == "power":
        sol = PowerSC(program, dead)

    elif source == "tso" and target == "pso":
        sol = PSOTSO(program, dead)
    elif source == "tso" and target == "rmo":
        sol = RMOTSO(program, dead)
    elif source == "tso" and target == "alpha":
        sol = AlphaTSO(program, dead)
    elif source == "tso" and target == "power":
        sol = PowerTSO(program, dead)

    elif source == "pso" and target == "rmo":
        sol = RMOPSO(program, dead)
    elif source == "pso" and target == "alpha":
        sol = AlphaPSO(program, dead)
    elif source == "pso" and target == "power":
        sol = PowerPSO(program, dead)

    elif source == "rmo" and target == "alpha":
        sol = AlphaRMO(program, dead)
    elif source == "rmo" and target == "power":
        sol = PowerRMO(program, dead)

    elif source == "alpha" and target == "rmo":
        sol = RMOAlpha(program, dead)
    elif source == "alpha" and target == "power":
        sol = PowerAlpha(program, dead)

    elif source == "cav10" and target == "power":
        sol = PowerCAV(program, dead)
    elif source == "power" and target == "cav10":
        sol = CAVPower(program, dead)

    else:
        print 'The model combination is not allowed. Plase select one combination from the paper.'
        return

    if sol == sat:
        print 'The program is not portable'
    else:
        print 'The program is portable'    

    return

if __name__ == "__main__":
    main(sys.argv[1:])
