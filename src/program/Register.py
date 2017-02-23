from types import *
from Expression import *
from z3 import Int

class Register(Expression):
    
    def __init__(self, name):
        assert(type(name) is StringType)
        self.name = name
        self.thread = None
    
    def __repr__(self):
        return self.name
    
    def __str__(self):
        return self.name
    
    ### For unrolling the while, we need to create deep copies of the sub-thread and this might create
    ### copies of the register, therefore we override the __deepcopy__ method for this class
    def __deepcopy__(self, memo):
        return self
    
    ### Since registers are local per thread, we assign a thread to them to use in the renaming
    ### We do not assign the whole thread, but its pid
    def setThread(self, t):
        #        assert (self.thread == None or self.thread == t.pid)
        self.thread = t.pid
        return self
    
    ### Returns a constraint representing the register after renaming to satisfy SA
    def encode(self, mapping):
        if self.thread == None: raise Exception("Threads should be assigned to events and registers before calling encode()")
        return Int("T%s_%s%s" %(str(self.thread), str(self.name), str(getLast(self, mapping))))

def getLast(x, mapping):
    """ Returns the last set value of x in mapping. """
    if not x in mapping.keys(): mapping[x] = 0
    return mapping[x]
