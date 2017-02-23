from Event import *

class Store(Event):
    
    def __init__(self, loc, reg):
        assert(isinstance(reg, Register) and isinstance(loc, Location))
        self.loc = loc
        self.reg = reg
        self.pid = None
        self.eid = None
        self.thread = None
        self.condLevel = 0
        self.SALoc = None
        self.SAreg = None
        self.mapLastMod = {}
        self.condReg = None
    
    def __str__(self):
        return "%s%s = %s" % ("  "*self.condLevel, str(self.loc), str(self.reg))
    
    def __repr__(self):
        return "E%s" % str(self.eid)
    
    def setMapLastMod(self, mapping):
        self.mapLastMod = mapping
        res = copy(self.mapLastMod)
        res[self.loc] = set([self])
        return res
    
    def getMapLastMod(self): return self.mapLastMod
    
    def getLastMod():
        if self.reg in self.mapLastMod.keys(): return set([self.mapLastMod[self.reg]])
        else: raise Exception('Problem with mapLastMod')