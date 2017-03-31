from Event import *

### Loads can only read from locations, any other kinf od thing (reg = Int or reg = Exp) is consider local
class Load(Event):

    def __init__(self, reg, loc):
        assert(isinstance(reg, Register) and isinstance(loc, Location))
        self.reg = reg
        self.loc = loc
        self.pid = None
        self.eid = None
        self.z3id = None
        self.thread = None
        self.condLevel = 0
        self.SAreg = None
        self.SAloc = None
        self.mapLastMod = {}
        self.condReg = None

    def __str__(self):
        return "%s%s <- %s" % ("  "*self.condLevel, self.reg, self.loc)

    def __repr__(self):
        return "E%s" % str(self.eid)

    def setMapLastMod(self, mapping={}):
        self.mapLastMod = mapping
        res = copy(self.mapLastMod)
        res[self.reg] = set([self])
        return res

    def getMapLastMod(self): return self.mapLastMod

    def getLastMod():
        if self.loc in self.mapLastMod.keys(): return set([self.mapLastMod[self.loc]])
        else: raise Exception('Problem with mapLastMod')