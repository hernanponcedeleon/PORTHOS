from Thread import *

### Event := Local | Load | Store
class Event(Thread):

    ### It does not have an __init__ since the corresponding one from Load or Store should be used

    def incCondLevel(self):
        """ Increments its conditional level. """
        self.condLevel += 1
        return self 

    def decCondLevel(self):
        """ Decrements the conditional level of itself and its sub-threads. """
        self.condLevel -= 1
        return self

    def setProgramsID(self, x):
        """ Sets its pid. """
        self.pid = x
        return x + 1

    def setEventsID(self, x):
        """ Stes its eid. """
        self.eid = x
        return x + 1

    def unroll(self, bound):
        return self

    def setCondReg(self, regs):
        self.condReg = regs
        return self

### This is a kind of representative for the events
def ev(e):
    assert(isinstance(e, Event))
    return "E%s" %(e.eid)