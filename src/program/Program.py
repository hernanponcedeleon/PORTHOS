from z3 import *
from types import *
from copy import copy, deepcopy
from itertools import product, combinations
from time import time
import random
import collections

from ControlFlow import *
from DataFlow import *

from Barrier import *
from Event import *
from If import *
from Init import *
from Load import *
from Local import *
from Location import *
from Register import *
from Seq import *
from Skip import *
from Store import *
from Thread import *
from While import *

### Integer variable to encode that ws is a total order
def wsVar(e): return Int("ws:L%s(%s)" %(e.loc, ev(e)))

### Integer variable to encode that po is a total order
def poVar(e, arch): return Int("%s_po:T%s(%s)" %(arch, e.thread, ev(e)))

### Integer variable to encode that ghb is a partial order
def ghbVar(e): return Int("ghb(%s)" %(ev(e)))

### Integer variable to encode that uniProc is acylic
def uniProcVar(e): return Int("up(%s)" %(ev(e)))

### Bool variable to encode that two events are related under rel
def edge(rel, e1, e2, arch=""): return Bool("%s%s(%s,%s)" %(rel, arch, ev(e1), ev(e2)))

### Bool variable to encode the edges of the cycle
def cycleEdge(rel, x, y): return Bool("Cycle:%s(%s,%s)" %(rel, ev(x), ev(y)))

### Bool variable to encode the nodes (events) of the cycle
def cycleVar(x): return Bool("Cycle(%s)" %(ev(x)))

def encodeALO(l):
    """ Encodes that AT LEAST ONE element in the list can be true. """
    assert(isinstance(l, list))
    if l == []: return False
    return Or(l)

def encodeEO(l):
    """ Encodes that EXACTLY one element in the list can be true. """
    assert(isinstance(l, list))
    if l == []: return False
    encoding = False
    for i in range(len(l)):
        rest = l[:i] + l[i+1:]
        rest = map(lambda e : Not(e), rest)
        rest.append(l[i])
        encoding = Or(encoding, And(rest))
    return encoding

def getEvents(t):
    assert(isinstance(t, Thread))
    if isinstance(t, Event): return [t]
    elif isinstance(t, Skip): return []
    elif isinstance(t, While): return getEvents(t.t1)
    elif isinstance(t, (If, Seq)): return getEvents(t.t1) + getEvents(t.t2)
    else: raise Exception ("Type error in getEvents")

class Program:

    def __init__(self, name=''):
        self.threads = list()
        self.name = name

    def __str__(self):
        return "\n".join("\nthread %d\n%s" % (i, str(x)) for i,x in enumerate(self.threads) if not isinstance(x, Init))

    def add(self, t):
        assert(isinstance(t, Thread))
        self.threads.append(t)
        return self

    def setID(self):
        pid, eid = 1, 1
        for t in self.threads:
            pid = t.setProgramsID(pid)
            eid = t.setEventsID(eid)
        return self

    def initialize(self, bound=1):
        #### add initialization of regs
        """ It initializes a multi-threaded program by setting locations to 0, adding IDs to threads and events and setting threads for events and registers. """
        unrolledThreads = list()
        for t in self.threads:
            newT = t.unroll(bound)
            unrolledThreads.append(newT)
        self.threads = unrolledThreads
        ### It adds events initializing the locations to 0
        locs = set([x.loc for x in filter(lambda e: isinstance(e, (Load, Store)), self.events())])
        for l in locs:
            self.add(Init(l))
        ### And then sets the IDs
        self.setID()
        for t in self.threads:
            t.setThread(t)
            t.setMapLastMod({})
            t.setCondReg(set())
            regs = set([x.reg for x in filter(lambda e: isinstance(e, (Local, Load, Store)), getEvents(t))])
            for r in regs: r.setThread(t)
        return self

    def events(self): return sum(map(getEvents, self.threads), [])

    def initEvents(self): return filter(lambda e: isinstance(e, Init), self.events())

    def storeEvents(self): return filter(lambda e: isinstance(e, Store), self.events())

    def loadEvents(self): return filter(lambda e: isinstance(e, Load), self.events())

    def encodeDF_RF(self):
        """ Encodes the fact that if a load read from store, then the values of the locations coincide. """
        enc = True
        for r in self.loadEvents():
            writeSameLoc = filter(lambda w: w.loc == r.loc, self.storeEvents() + self.initEvents())
            sameValues = And(map(lambda w: Implies(edge("rf", w, r), r.SAloc == w.SAloc), writeSameLoc))
            enc = And(enc, sameValues)
        return enc

def encode(p):
    assert(isinstance(p, Program))
    ### This is the global mapping used for renaming the variables
    indexes = {}
    ### DF encodes the relations between variables in different threads
    DF = True
    for t in p.threads:
        (enc, indexes) = encodeDF(t, indexes)
        DF = And(DF, enc)
    ### We encode control flow, dataflow within and between threads, the memory model and the fact that
    ### the "highest" threads are active
    return And(And([encodeCF(t) for t in p.threads]),
               DF, p.encodeDF_RF(), #p.encodeMM(),
               And([Bool(repr(t)) for t in  p.threads]))

def randomProg(locs, regs, thrds, inst):

    locsPool = []
    for x in locs:
        locsPool.append(Location(x))

    regsPool = []
    for x in regs:
        regsPool.append(Register(x))

    usedRegsPool = {}
    for i in range(thrds):
        usedRegsPool[i] = []

    dic = {}
    for t in range(thrds):
        dic[t] = None

    for i in range(inst):
	if i < thrds: proc = i
	else: proc = random.randrange(0, thrds)
        if usedRegsPool[proc] != []:
            weighted_choices = [('W', 4), ('R', 3), ('L', 2), ('B', 1)]
        else:
            weighted_choices = [('R', 3), ('L', 3)]
        population = [val for val, cnt in weighted_choices for i in range(cnt)]
        op = random.choice(population)
        loc = random.choice(locsPool)
        reg = random.choice(regsPool)
	if op == "B": e = Mfence()
        if op == "SF": e = Sync()
        if op == "WF": e = Lwsync()
        elif op == "W": e = Store(loc, random.choice(usedRegsPool[proc]))
        elif op == "R": e = Load(reg, loc)
        elif op == "L": e = Local(reg, Expression(random.choice([1,2,3,4,5])))
        if dic[proc] == None:
            dic[proc] = Local(reg, Expression(random.choice([1,2,3,4,5])))
            usedRegsPool[proc].append(reg)
        else: dic[proc] = Seq(dic[proc], e)

    pr = Program()
    for d in dic.keys():
        pr.add(dic[d])

    return pr

def exportLitmus(m, name, satSolution):
    events = m.events()
    locs = set([x.loc for x in filter(lambda e: isinstance(e, (Load, Store, Init)), m.events())])

    procDic = collections.defaultdict(dict)
    regsDic = collections.defaultdict(dict)
    for t in m.threads:
        procDic[t.pid] = collections.defaultdict(dict)
        regsDic[t.pid] = set()
    for e in events:
        if isinstance(e, Init): continue
        elif isinstance(e, Sync):
                procDic[e.thread][e.eid] = "sync"
        elif isinstance(e, Lwsync):
                procDic[e.thread][e.eid] = "lwsync"
        elif isinstance(e, Mfence):
		procDic[e.thread][e.eid] = "MFENCE"
	elif isinstance(e, Load):
            procDic[e.thread][e.eid] = "MOV %s,[%s]" % (e.reg.name, e.loc.name)
            regsDic[e.thread].add(e.reg)
        elif isinstance(e, Store):
	    procDic[e.thread][e.eid] = "MOV [%s],%s" % (e.loc.name, e.reg.name)
            regsDic[e.thread].add(e.reg)
	if isinstance(e, Local):
	    procDic[e.thread][e.eid] = "MOV %s,$%s" % (e.reg.name, str(e.exp))
            (regsDic[e.thread]).add(e.reg)

    count = 0
    regs = []
    for t in regsDic.keys():
        for r in regsDic[t]:
            regs.append((count, r))
        count += 1

    litmus = "X86 " + name + "-" + satSolution + "\n"
    litmus += "{ \n"
    for l in locs:
        litmus += l.name + "=0; "
    litmus += "\n}\n "
    for pid, p in enumerate(filter(lambda e: not isinstance(e, Init), m.threads)): 
        if p == m.threads[0]:
            litmus += "P" + str(pid) + "\t\t"
        else:
            litmus += "| P" + str(pid) + "\t\t"
    litmus += ";\n"
    for i in range(len(filter(lambda e : not isinstance(e, Init), events))):
        for t in filter(lambda e: not isinstance(e, Init), m.threads):
            if t == m.threads[0]:
                if procDic[t.pid][i+1] == "MFENCE":
                    litmus += " " + procDic[t.pid][i+1] + "\t\t"
                elif procDic[t.pid][i+1] != {}:
                    litmus += " " + procDic[t.pid][i+1] + "\t"
                else:
                    litmus += "\t\t"
            else:
                if procDic[t.pid][i+1] != {}:
                    litmus += "| " + procDic[t.pid][i+1] + "\t"
                else:
                    litmus += "| \t\t"
        litmus += ";\n"
    writeLocs = "\nlocations ["
    for l in locs:
        writeLocs += '%s;' %str(l)
    litmus += '%s]\n' %writeLocs        
#    writeRegs = "exists (%s:%s=0" %(regs[0][0], regs[0][1])
#    for r in regs[1:]:
#        writeRegs += "/\ %s:%s=0" %(r[0], r[1])
#    litmus += '%s)\n' %writeRegs

    return litmus

