from Thread import *
from Skip import * 

class Seq(Thread):

    def __init__(self, t1, t2):
        assert(isinstance(t1, Thread) and isinstance(t2, Thread))
        self.t1 = t1
        self.t2 = t2
        self.pid = None
        self.thread = None
        self.condLevel = 0

    def __str__(self):
        if isinstance(self.t2, Skip):
            return str(self.t1)
        return "%s;\n%s" % (str(self.t1), str(self.t2))
    
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

    def unroll(self, bound):
        self.t1 = self.t1.unroll(bound)
        self.t2 = self.t2.unroll(bound)
        return self

    def setMapLastMod(self, mapping={}):
        newMapping = self.t1.setMapLastMod(mapping)
        return self.t2.setMapLastMod(newMapping)

    def setCondReg(self, regs):
        self.t1.setCondReg(regs)
        self.t2.setCondReg(regs)
        return self

    def setThread(self, t):
        self.thread = t.pid
        self.t1.setThread(t)
        self.t2.setThread(t)
