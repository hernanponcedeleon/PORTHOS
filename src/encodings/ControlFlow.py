from Event import *
from Skip import *
from Seq import *
from If import *

from z3 import Bool, And, Or, Implies, Xor

def encodeCF(t):
    """ Encodes the control flow of the program. """
    assert(isinstance(t, Thread))
    if isinstance(t, Seq):
        ### If some sub-thread is active, the sequence is active
        ### If the sequence is active, both sub-threadss are active
        ### And we encode recursively for the sub-threads
        return And(Implies(Or(Bool(repr(t.t1)), Bool(repr(t.t2))), Bool(repr(t))),
                   Implies(Bool(repr(t)), And(Bool(repr(t.t1)), Bool(repr(t.t2)))),
                   encodeCF(t.t1),
                   encodeCF(t.t2))
    elif isinstance(t, If):
        ### When the if is active, exaclty one of the sub-threads is active
        ### When some sub-thread is active, then the if is active
        ### And we encode recursively for the sub-threadss
        return And(Implies(Bool(repr(t)), Xor(Bool(repr(t.t1)), Bool(repr(t.t2)))),
                   Implies(Or(Bool(repr(t.t1)), Bool(repr(t.t2))), Bool(repr(t))),
                   encodeCF(t.t1),
                   encodeCF(t.t2))
    elif isinstance(t, Event):
        ### The thread is active iff the event is active
        return Bool(repr(t)) == Bool(ev(t))
    elif isinstance(t, Skip):
        ### Skip programs do not impose things in the control flow
        return True
    else: raise Exception("Type error in encodeCF()")
