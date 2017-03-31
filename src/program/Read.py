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

    def __str__(self): return "%s%s = %s.load(%s) -- %s" %("  "*self.condLevel, self.reg, self.loc, self.type, self.eid)

    def compileTo(self, bound, arch):
        return self.atomicToLowLevel(arch)

    def atomicToLowLevel(self, arch, compiler="llvm"):
        ld = Load(self.reg, self.loc)
        ld.z3id = self.eid
        if compiler != "llvm":
            raise Exception ('Compiler %s is not supported' %compiler)
        if arch in ["sc", "tso", "pso", "rmo", "alpha"]:
            return ld
        elif arch in ["power", "cav10"]:
            if self.type == "sc": return Seq(Sync(), Seq(ld, Lwsync()))
            elif self.type in ["rx", "na"]: return ld
            elif self.type in ["con", "ack"]: return Seq(ld, Lwsync())
            else: raise Exception ('Error in the atomic operation type of %s' %self)
        else: raise Exception ('Error in the architecture %s' %arch)
