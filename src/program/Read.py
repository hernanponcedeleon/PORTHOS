from Event import *
from Load import *
from Seq import *
from Barrier import *

class Read(Event):

    def __init__(self, reg, loc, type):
        self.reg = reg
        self.loc = loc
        self.type = type
        self.condLevel = 0
        self.eid = None

    def __str__(self): return "%s%s = %s.load(%s)" %("  "*self.condLevel, self.reg, self.loc, self.type)

    def compileTo(self, bound):
        return self.atomicToLowLevel()

    def atomicToLowLevel(self):
        ld = Load(self.reg, self.loc)
        ld.z3id = self.eid
        if self.type == "sc": return Seq(Sync(), Seq(ld, Lwsync()))
        elif self.type in ["rx", "na"]: return ld
        elif self.type in ["con", "acq"]: return Seq(ld, Lwsync())
        else: raise Exception ('Error in the atomic operation type of %s' %self)