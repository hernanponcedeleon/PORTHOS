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

    def __str__(self): return "%s%s.store(%s, %s) -- %s" %("  "*self.condLevel, self.loc, self.reg, self.type, self.eid)

    def compileTo(self, bound, arch):
        return self.atomicToLowLevel(arch)

    def atomicToLowLevel(self, arch, compiler="llvm"):
        st = Store(self.loc, self.reg)
        st.z3id = self.eid
        if compiler != "llvm":
            raise Exception ('Compiler %s is not supported' %compiler)
        if arch in ["sc", "tso", "pso", "rmo", "alpha"]:
            if self.type == "sc": return Seq(st, Sync())
            else: return st
        elif arch in ["power", "cav10"]:
            if self.type == "sc": return Seq(Sync(), st)
            elif self.type == "rx": return st
            elif self.type == "rel": return Seq(Lwsync(), st)
            else: raise Exception ('Error in the atomic operation type of %s' %self)
        else: raise Exception ('Error in the architecture %s' %arch)
