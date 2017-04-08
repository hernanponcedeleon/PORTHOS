from Event import *
from Store import *
from Seq import *
from Barrier import *

class Write(Event):

    def __init__(self, loc, reg, type):
        self.loc = loc
        self.reg = reg
        self.type = type
        self.condLevel = 0
        self.eid = None

    def __str__(self): return "%s%s.store(%s, %s)" %("  "*self.condLevel, self.loc, self.reg, self.type)

    def compileTo(self, bound):
        return self.atomicToLowLevel()

    def atomicToLowLevel(self):
        st = Store(self.loc, self.reg)
        st.z3id = self.eid
        if self.type == "sc": return Seq(Sync(), Seq(st, Mfence()))
        elif self.type == "rx": return st
        elif self.type == "rel": return Seq(Lwsync(), st)
        else: raise Exception ('Error in the atomic operation type of %s' %self)
