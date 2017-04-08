from Register import *
from Location import *
from copy import copy, deepcopy

### Thread := Event | Skip | If Predicate Thread Thread | Seq Thread Thread.
class Thread:

    ### It does not have an __init__ since the corresponding one from Load, Store, etc should be used

    def __str__(self): return "P%s" % self.pid

    def __repr__(self): return "P%s" % self.pid

    ### All the events "belong" to the "highest" thread in the sub-typing chain, i.e. they belong to the
    ### thread that is added to the multithreaded program
    ### We do not assign the whole thread, but its pid
    def setThread(self, t):
        self.thread = t.pid
        return self

    def compileTo(self, bound): return self