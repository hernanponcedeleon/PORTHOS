#!/usr/bin/env python
#!~/Documents/tools/pypy2-v5.3.0-osx64/bin/pypy

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
                outputfile = inputfile.split("/")[-1].split(".pts")[0]
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

    print "Checking portability between %s and %s %s" %(bcolors.OKBLUE + source + bcolors.ENDC, bcolors.OKBLUE + target + bcolors.ENDC, "with deadness" if dead else "")

    (sol, model) = portability(program, source, target, dead)

    if sol == sat:
        print bcolors.FAIL + 'The program is not portable' + bcolors.ENDC
    else:
        print bcolors.OKGREEN + 'The program is portable' + bcolors.ENDC

    if outputfile != None and model != None:
        program.write('%s.dot' %outputfile, model, map(lambda r: "%s(" %r, show))
        print "Output written to %s.dot" %outputfile
    return

if __name__ == "__main__":
    main(sys.argv[1:])
