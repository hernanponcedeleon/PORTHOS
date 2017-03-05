#!/usr/bin/env python

import sys, getopt
sys.path.append('./mcm/')
sys.path.append('./program/')
sys.path.append('./parsers/')
sys.path.append('./encodings/')
from ParserPorthos import *
from ParserAssembly import *
from Models import *
from z3 import *

class bcolors:
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def main(argv):

    inputfile = None
    outputfile = None
    source = None
    target = None
    show = []
    dead = False
    verbose = False
    try:
        opts, args = getopt.getopt(argv,"p:i:os:t:dv", ["print="])
    except getopt.GetoptError:
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-i":
            inputfile = arg
        elif opt == "-o":
            if inputfile.endswith('.litmus'):
                outputfile = inputfile.split("/")[-1].split(".litmus")[0]
            else:
                outputfile = inputfile.split(".pts")[0]
        elif opt == "-s":
            source = arg
        elif opt == "-t":
            target = arg
        elif opt in ["-p", "--print"]:
            show = arg.split(",")
        elif opt == "-d":
            dead = True
        elif opt == "-v":
            verbose = True
    if inputfile == None:
        print bcolors.FAIL + "No input file loaded." + bcolors.ENDC
        sys.exit()

    if not (source in ["sc", "tso", "pso", "rmo", "alpha", "power", "cav10"]):
        print bcolors.FAIL + "Source model is not valid." + bcolors.ENDC
        print "Select between sc, tso, pso, rmo, alpha, power, cav10"
        sys.exit()
    if not (target in ["tso", "pso", "rmo", "alpha", "power", "cav10"]):
        print bcolors.FAIL + "Target model is not valid." + bcolors.ENDC
        print "Select between tso, pso, rmo, alpha, power, cav10"
        sys.exit()

    if inputfile.endswith('.litmus'):
        program = parseLitmus(inputfile)
        ### The parser already creates the initial writes, so no need to initialize
    elif inputfile.endswith('.pts'):
        program = parsePorthosFile(inputfile)
        program.initialize()
    else:
        print bcolors.FAIL + 'Input is not a .litmus or .pts file' + bcolors.ENDC
        sys.exit()

    if verbose:
        print program

    print "Checking portability between %s and %s" %(bcolors.OKBLUE + source + bcolors.ENDC, bcolors.OKBLUE + target + bcolors.ENDC)

    if source == "sc" and target == "tso":
         (sol, model) = TSOSC(program, dead)
    elif source == "sc" and target == "pso":
         (sol, model) = PSOSC(program, dead)
    elif source == "sc" and target == "rmo":
         (sol, model) = RMOSC(program, dead)
    elif source == "sc" and target == "alpha":
         (sol, model) = AlphaSC(program, dead)
    elif source == "sc" and target == "power":
         (sol, model) = PowerSC(program, dead)

    elif source == "tso" and target == "pso":
         (sol, model) = PSOTSO(program, dead)
    elif source == "tso" and target == "rmo":
         (sol, model) = RMOTSO(program, dead)
    elif source == "tso" and target == "alpha":
         (sol, model) = AlphaTSO(program, dead)
    elif source == "tso" and target == "power":
         (sol, model) = PowerTSO(program, dead)

    elif source == "pso" and target == "rmo":
         (sol, model) = RMOPSO(program, dead)
    elif source == "pso" and target == "alpha":
         (sol, model) = AlphaPSO(program, dead)
    elif source == "pso" and target == "power":
         (sol, model) = PowerPSO(program, dead)

    elif source == "rmo" and target == "alpha":
         (sol, model) = AlphaRMO(program, dead)
    elif source == "rmo" and target == "power":
         (sol, model) = PowerRMO(program, dead)

    elif source == "alpha" and target == "rmo":
         (sol, model) = RMOAlpha(program, dead)
    elif source == "alpha" and target == "power":
         (sol, model) = PowerAlpha(program, dead)

    elif source == "cav10" and target == "power":
         (sol, model) = PowerCAV(program, dead)
    elif source == "power" and target == "cav10":
         (sol, model) = CAVPower(program, dead)

    else:
        print bcolors.FAIL + 'The model combination is not allowed.' + bcolors.ENDC
        sys.exit()

    if sol == sat:
        print bcolors.FAIL + 'The program is not portable' + bcolors.ENDC
    else:
        print bcolors.OKGREEN + 'The program is portable' + bcolors.ENDC

    if outputfile != None and model != None:
        if verbose: print "Output written to %s.dot" %outputfile
        program.write('%s.dot' %outputfile, model, map(lambda r: "%s(" %r, show))

    return

if __name__ == "__main__":
    main(sys.argv[1:])
