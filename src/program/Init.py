from Event import *

class Init(Event):

    def __init__(self, loc):
        assert(isinstance(loc, Location))
        self.loc = loc
        self.pid = None
        self.eid = None
        self.z3id = id(self)
        self.thread = None
        ### When the dataflow is encoded, we save the variable numbering for future uses, for example to encode
        ### that if a load read-from a store, then the values of the locations coincide
        self.SAloc = None
        self.mapLastMod = {}
        self.condReg = None

    def __str__(self):
        return "%s = 0" %(self.loc)

    def __repr__(self):
        return "P%s" % str(self.pid)

    def setMapLastMod(self, mapping={}):
        self.mapLastMod = mapping
        res = copy(self.mapLastMod)
        res[self.loc] = set([self])
        return res