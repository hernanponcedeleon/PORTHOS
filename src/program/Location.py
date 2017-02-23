from types import *
from z3 import Int

class Location:
    
    def __init__(self, name):
        assert(type(name) is StringType)
        self.name = name
    
    def __repr__(self):
        return self.name
    
    def __str__(self):
        return self.name
    
    ### For unrolling the while, we need to create deep copies of the sub-thread and this might create
    ### copies of the location, therefore we override the __deepcopy__ method for this class
    def __deepcopy__(self, memo):
        return self
    
    ### Returns a constraint representing the location after renaming to satisfy SA. It is alwasy a fresh variable
    ### since SA get fresh ones on the left and we get fresh ones on the right to allow reading from any event
    def encode(self, mapping): return Int("%s%s" %(str(self.name), str(getFresh(self, mapping))))

def getFresh(x, mapping):
    """ Returns a fresh value for x and set it in mapping. """
    if not x in mapping.keys(): mapping[x] = 0
    else: mapping[x] += 1
    return mapping[x]

