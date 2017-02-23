#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, getopt
import pyparsing as pyp
from Program import *

newline = pyp.LineEnd()
symbols = "!\"@#€%&/|()[]$~=?+`´^¨*',;.:-_><"
digits = "0123456789"
alphanum = pyp.alphas + digits
locs = "xyzabct"
letter = pyp.Or([pyp.Word(x) for x in pyp.alphas if len(x) == 1])
locations = letter(locs)
x86Locs = pyp.Group("[" + locations + "]")
const = pyp.Word(digits)
x86Reg = pyp.Group("E" + letter + "X")
x86Const = pyp.Group("$" + pyp.Word(digits))
registers = pyp.Group("r" + const)
architectures = pyp.Or([pyp.Literal("PPC"), pyp.Literal("X86")])

# define Header grammar
Header = architectures + pyp.OneOrMore(pyp.OneOrMore(pyp.Word(alphanum + symbols)) + newline)

# define Init grammar
assign = pyp.Or([pyp.Group(pyp.Word(alphanum) + ":" + registers + "=" + pyp.Or([locations, const]) + ";"), pyp.Group(letter + "=" + pyp.Word(digits) + ";")])
Init = pyp.Literal('{') + pyp.OneOrMore(assign) + pyp.Literal('}')

procName = pyp.Group("P" + const)
Procs = pyp.OneOrMore(procName + pyp.Optional("|")) + ";"

# define Events grammar
eEvent = pyp.Literal(' ')
wEvent = pyp.Group("MOV" + x86Locs  + "," + x86Reg)
rEvent = pyp.Group("MOV" + x86Reg + "," + pyp.Or([x86Const, x86Locs]))
bEvent = pyp.Group(pyp.Literal("MFENCE"))
stwEvent = pyp.Group("stw" + registers  + ",0(" + registers + ")")
lwzEvent = pyp.Group("lwz" + registers  + ",0(" + registers + ")")
liEvent = pyp.Group("li" + registers + "," + const)
addiEvent = pyp.Group("addi" + registers + "," + registers + "," + const)
copyEvent = pyp.Group("mr" + registers + "," + registers)
xorEvent = pyp.Group("xor" + registers + "," + registers + "," + registers)
syncEvent = pyp.Group(pyp.Literal("sync"))
lwsyncEvent = pyp.Group(pyp.Literal("lwsync"))
isyncEvent = pyp.Group(pyp.Literal("isync"))
cmpEvent = pyp.Group("cmpw" + registers + "," + registers)
beqEvent = pyp.Group("beq" + pyp.Word(pyp.alphas) + pyp.Word(digits))
guardEvent = pyp.Group(pyp.Word(alphanum) + ":")

event = pyp.Or([eEvent, wEvent, rEvent, bEvent, stwEvent, lwzEvent, liEvent, copyEvent, addiEvent, xorEvent, syncEvent, lwsyncEvent, isyncEvent, cmpEvent, beqEvent, guardEvent])
Events = pyp.OneOrMore(pyp.OneOrMore(pyp.Or([event, pyp.Literal("|")])) + pyp.Literal(";"))

Prog = pyp.Group(Header) + pyp.Group(Init) + pyp.Group(Procs) + pyp.Group(Events)

def string2Event(s, initT, locations, registers):
    if "MOV" == s[0]:
        if s[1][0] == "[":
            if "".join(s[3]) in registers.keys():
                reg = registers["".join(s[3])]
            else:
                reg = Register("".join(s[3]))
                registers["".join(s[3])] = reg
        else:
            if "".join(s[1]) in registers.keys():
                reg = registers["".join(s[1])]
            else:
                reg = Register("".join(s[1]))
                registers["".join(s[1])] = reg
        if "$" in "".join(s[3]):
            const = Expression(int(s[3][1]))
            return (Local(reg, const), locations, registers)
        if s[1][0] == "[":
            locName = s[1][1]
            if locName in locations.keys():
                loc = locations[locName]
            else:
                locations[locName] = Location(locName)
                loc = locations[locName]
            return (Store(loc, reg), locations, registers)
        else:
            locName = s[3][1]
            if locName in locations.keys():
                loc = locations[locName]
            else:
                locations[locName] = Location(locName)
                loc = locations[locName]
            return (Load(reg, loc), locations, registers)
    if "stw" == s[0]:
        if "".join(s[1]) in registers.keys():
            reg = registers["".join(s[1])]
        else:
            reg = Register("".join(s[1]))
            registers["".join(s[1])] = reg
        regLoc = ''.join(s[3])
        if initT[regLoc] in locations.keys():
            loc = locations[initT[regLoc]]
        else:
            locations[initT[regLoc]] = Location(initT[regLoc])
            loc = locations[initT[regLoc]]
        return (Store(loc, reg), locations, registers)
    elif "lwz" == s[0]:
        if "".join(s[1]) in registers.keys():
            reg = registers["".join(s[1])]
        else:
            reg = Register("".join(s[1]))
            registers["".join(s[1])] = reg
        regLoc = ''.join(s[3])
        if initT[regLoc] in locations.keys():
            loc = locations[initT[regLoc]]
        else:
            locations[initT[regLoc]] = Location(initT[regLoc])
            loc = locations[initT[regLoc]]
        return (Load(reg, loc), locations, registers)
    elif "li" == s[0]:
        if "".join(s[1]) in registers.keys():
            reg = registers["".join(s[1])]
        else:
            reg = Register("".join(s[1]))
            registers["".join(s[1])] = reg
        const = Expression(int(s[3]))
        return (Local(reg, const), locations, registers)
    elif "addi" == s[0]:
        if "".join(s[1]) in registers.keys():
            reg = registers["".join(s[1])]
        else:
            reg = Register("".join(s[1]))
            registers["".join(s[1])] = reg
        if "".join(s[3]) in registers.keys():
            reg2 = registers["".join(s[3])]
        else:
            reg2 = Register("".join(s[3]))
            registers["".join(s[3])] = reg2
        return (Local(reg, Expression(reg2,'+',1)), locations, registers)
    elif "mr" == s[0]:
        if "".join(s[1]) in registers.keys():
            reg = registers["".join(s[1])]
        else:
            reg = Register("".join(s[1]))
            registers["".join(s[1])] = reg
        if "".join(s[3]) in registers.keys():
            reg2 = registers["".join(s[3])]
        else:
            reg2 = Register("".join(s[3]))
            registers["".join(s[3])] = reg2
        return (Local(reg, reg2), locations, registers) 
    elif "xor" == s[0]:
        if "".join(s[1]) in registers.keys():
            reg = registers["".join(s[1])]
        else:
            reg = Register("".join(s[1]))
            registers["".join(s[1])] = reg
        if "".join(s[3]) in registers.keys():
            reg2 = registers["".join(s[3])]
        else:
            reg2 = Register("".join(s[3]))
            registers["".join(s[3])] = reg2
        if "".join(s[5]) in registers.keys():
            reg3 = registers["".join(s[5])]
        else:
            reg3 = Register("".join(s[5]))
            registers["".join(s[5])] = reg3
        return (Local(reg, Expression(reg2,'xor',reg3)), locations, registers)
    elif "MFENCE" == s[0]:
        return (Mfence(), locations, registers)
    elif "sync" == s[0]:
        return (Sync(), locations, registers)
    elif "lwsync" == s[0]:
        return (Lwsync(), locations, registers)
    elif "isync" == s[0]:
        return (Isync(), locations, registers)
    elif "cmpw" == s[0]:
        if "".join(s[1]) in registers.keys():
            reg1 = registers["".join(s[1])]
        else:
            reg1 = Register("".join(s[1]))
            registers["".join(s[1])] = reg1
        if "".join(s[3]) in registers.keys():
            reg2 = registers["".join(s[3])]
        else:
            reg2 = Register("".join(s[3]))
            registers["".join(s[3])] = reg2
        return (Predicate(reg1,'==',reg2), locations, registers)
    else: raise Exception("Parsing problem! with %s" %s[0])

def list2Seq(l, initT, locations, registers):
    if len(l) == 1:
        return string2Event(l[0], initT, locations, registers)
    elif l[0][0] == "cmpw":
        (pred, locations, registers) = string2Event(l[0], initT, locations, registers)
        (t1, locations, registers) = list2Seq(l[3:], initT, locations, registers)
        return (If(pred, t1, Skip()), locations, registers)
    else:
        (t1, locations, registers) = string2Event(l[0], initT, locations, registers)
        (t2, locations, registers) = list2Seq(l[1:], initT, locations, registers)
        return (Seq(t1, t2), locations, registers)

def parseLitmus(filename):
    """ Parses a litmus test in HERD's format and loaded in memory as a Program. """
    f = open(filename,'r')
    text = "".join(f.readlines())
    parsed = Prog.parseString(text)
    
    nextL = parsed[1]
    init = {}
    count = 0

    for x in nextL:
        if x != "{" and x != "}":
            if not ':' == x[1]: continue
            if "P0" in x[0]: count = 0
            elif "P1" in x[0]: count = 1
            elif "P2" in x[0]: count = 2
            elif "P3" in x[0]: count = 3
            elif "P4" in x[0]: count = 4
            else: count = int(x[0])
            if not count in init.keys(): init[count] = {}
            reg = "".join(x[2])
            init[count][reg] = x[4]
    threads = {}

    numProcs = parsed[2]
    for x in range(len([p for p in numProcs if len(p) > 1])):
        threads[x] = []

    threadCount = 0
    for x in parsed[3]:
        if x == "|": threadCount += 1
        elif x == ";": threadCount = 0
        else: threads[threadCount].append(x)

    prog = Program(filename)
    locations = {}
    for t in threads.keys():
        if t not in init.keys(): init[t]={}
        (thread, locations, registers) = list2Seq(threads[t], init[t], locations, {})
        for x in init[t].keys():
            if x not in init[t].keys(): init[t][x]=0
            if "t" not in init[t][x] and "x" not in init[t][x] and "y" not in init[t][x] and "z" not in init[t][x] and "a" not in init[t][x] and "b" not in init[t][x] and "c" not in init[t][x]:
                if x in registers.keys():
                    reg = registers[x]
                else:
                    reg = Register(x)
                    registers[x] = reg
                thread = Seq(Local(reg, Expression(int(init[t][x]))), thread)
        prog.add(thread)
    prog.initialize()
    return prog
