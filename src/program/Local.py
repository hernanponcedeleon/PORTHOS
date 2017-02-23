from Event import * 

class Local(Event):
    
    def __init__(self, reg, exp):
        assert(isinstance(reg, Register) and isinstance(exp, Expression))
        self.reg = reg
        self.exp = exp
        self.pid = None
        self.eid = None
        self.thread = None
        self.condLevel = 0
        self.SAreg = None
        self.SAexp = None
        self.mapLastMod = {}
        self.condReg = None
    
    def __str__(self):
        return "%s%s <- %s" % ("  "*self.condLevel, str(self.reg), str(self.exp))
    
    def __repr__(self):
        return "E%s" % str(self.eid)
    
    def setMapLastMod(self, mapping={}):
        self.mapLastMod = mapping
        res = copy(self.mapLastMod)
        res[self.reg] = set([self])
        return res
    
    def getMapLastMod(self): return self.mapLastMod
    
    def getLastMod():
        res = []
        for r in self.exp.getRegs():
            if r in self.mapLastMod.keys(): res.append(r)
            else: raise Exception('Problem with mapLastMod')
        return set(res)