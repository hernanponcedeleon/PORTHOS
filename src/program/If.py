from Thread import *
from Skip import *

class If(Thread):

    def __init__(self, pred, t1, t2):
        assert(isinstance(pred, Predicate) and isinstance(t1, Thread) and isinstance(t2, Thread))
        self.pred = pred
        self.t1 = t1
        self.t2 = t2
        self.pid = None
        self.thread = None
        ### The conditional level is used for pretty printing
        self.condLevel = 0
        self.t1.incCondLevel()
        self.t2.incCondLevel()

    def __str__(self):
        if isinstance(self.t2, Skip):
            return "%sif %s {\n%s\n%s}" % ("  "*self.condLevel, str(self.pred), str(self.t1), "  "*self.condLevel)
        return "%sif %s {\n%s%s\n%s}\n%selse {\n%s%s\n%s}" % ("  "*self.condLevel, str(self.pred), "  "*self.condLevel, str(self.t1), "  "*self.condLevel, "  "*self.condLevel, "  "*self.condLevel, str(self.t2), "  "*self.condLevel)

    def incCondLevel(self):
        """ Increments the conditional level of itself and its sub-threads. """
        self.condLevel += 1
        self.t1.incCondLevel()
        self.t2.incCondLevel()
        return self

    def decCondLevel(self):
        """ Decrements the conditional level of itself and its sub-threads. """
        self.condLevel -= 1
        self.t1.decCondLevel()
        self.t2.decCondLevel()
        return self

    def setProgramsID(self, x):
        """ Sets the pid of itself and its sub-threads. """
        ### Each x is different, that's why we return it and updated on the left side
        x = self.t1.setProgramsID(x)
        x = self.t2.setProgramsID(x)
        self.pid = x
        return x + 1

    def setEventsID(self, x):
        """ Sets the eid of its sub-threads. """
        ### Each x is different, that's why we return it and updated on the left side
        x = self.t1.setEventsID(x)
        x = self.t2.setEventsID(x)
        return x

    def compileTo(self, bound, arch):
        self.t1 = self.t1.compileTo(bound, arch)
        self.t2 = self.t2.compileTo(bound, arch)
        return self

    def setMapLastMod(self, mapping={}):
        map1 = self.t1.setMapLastMod(copy(mapping))
        map2 = self.t2.setMapLastMod(copy(mapping))
        return mergeMapLastMod(map1, map2)

    def setCondReg(self, regs):
        newRegs = regs.union(getRegs(self.pred))
        self.t1.setCondReg(newRegs)
        self.t2.setCondReg(newRegs)
        return self

    def setThread(self, t):
        self.thread = t.pid
        self.t1.setThread(t)
        self.t2.setThread(t)

def getRegs(exp):
    #    assert(isinstance(exp, (int, Expression)))
    if isinstance(exp, int): return set()
    if isinstance(exp, Register): return set([exp])
    if isinstance(exp, Expression) and isinstance(exp.v1, int): return set()
    elif isinstance(exp, Expression): return getRegs(exp.v1).union(getRegs(exp.v2))
    elif isinstance(exp, Predicate): return getRegs(exp.p1).union(getRegs(exp.p2))
    else: raise Exception("Problem with getRegs")

def mergeMapLastMod(map1, map2):
    newMap = copy(map1)
    for x in map2.keys():
        if x in newMap.keys(): newMap[x] = newMap[x].union(map2[x])
        else: newMap[x] = map2[x]
    return newMap
