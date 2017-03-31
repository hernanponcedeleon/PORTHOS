from Thread import *
from If import *
from Skip import *
from Seq import *

class While(Thread):

    def __init__(self, pred, t):
        assert(isinstance(pred, Predicate) and isinstance(t, Thread))
        self.pred = pred
        self.t1 = t
        self.pid = None
        ### The conditional level is used for pretty printing
        self.condLevel = 0
        self.t1.incCondLevel()
 
    def __str__(self):
        return "%swhile %s {\n%s\n%s}" % ("  "*self.condLevel, str(self.pred), str(self.t1), "  "*self.condLevel)

    def incCondLevel(self):
        """ Increments the conditional level of itself and its sub-threads. """
        self.condLevel += 1
        self.t1.incCondLevel()
        return self

    def decCondLevel(self):
        """ Decrements the conditional level of itself and its sub-threads. """
        self.condLevel -= 1
        self.t1.decCondLevel()
        return self

    def setProgramsID(self, x):
        """ Sets the pid of itself and its sub-threads. """
        ### Each x is different, that's why we return it and updated on the left side
        x = self.t1.setProgramsID(x)
        self.pid = x
        return x + 1

    def setEventsID(self, x):
        """ Sets the eid of its sub-threads. """
        ### Each x is different, that's why we return it and updated on the left side
        x = self.t1.setEventsID(x)
        return x

    def compileTo(self, bound, arch):
        if bound == 0:
            cLevel = self.condLevel
            self = Skip()
            ### The skip inherits the condLevel
            self.conLevel = cLevel
        else:
            t = deepcopy(self.t1)
            t.decCondLevel()
            t = t.compileTo(bound, arch)
            cLevel = self.condLevel
            self = If(self.pred, Seq(t, self.compileTo(bound -1 , arch)), Skip())
            ### The if inherits the conLevel of the While
            self.condLevel = cLevel
        return self
