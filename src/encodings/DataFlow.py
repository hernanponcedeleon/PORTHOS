from Init import *
from Load import *
from Local import *
from Store import *
from Barrier import *
from Seq import *
from If import *
from While import *

from copy import copy
from z3 import Int, Bool, Implies, And, Or, Not

def encodeDF(t, localMap):
    """ Encodes the data flow of the thread. """
    ### The localMap is used to rename variables to satisfy dymanic single assignement
    ### i.e. variables can have the same value if they belong to different branchees of an if
    ### For this we need to copy the localMap to pass to the differen sub-threads of an if
    ### and we need to merge the copies of the maps with the maximal values (this is done by mergeMaps)
    ### We need to return also the map for the merging
    ### Since one branch may have less occurences of a variable than other, we might need to encode
    ### x_{i+1} = x_i in some cases (this is done by encodeMissingIndexes). See page 191 of the paper 
    ### "Exploration of the Capabilities of Constraint Programming for Software Verification" for details

    assert(isinstance(t, Thread))
    if isinstance(t, Init):
        if t.thread == None: raise Exception("Threads should be assigned to events and registers before calling encode()")
        ### Since init events are always active, the value of the location is 0
        loc = Int("%s%s" %(str(t.loc), str(getFresh(t.loc, localMap))))
        enc = loc == 0
        t.SAloc = loc
    elif isinstance(t, Store):
        if t.thread == None: raise Exception("Threads should be assigned to events and registers before calling encode()")
        ### If the event is active, the value of the location and the register coincide
        reg = Int("T%s_%s%s" %(str(t.thread), str(t.reg), str(getLast(t.reg, localMap))))
        loc = Int("%s%s" %(str(t.loc), str(getFresh(t.loc, localMap))))
        enc = Implies(Bool(ev(t)), loc == reg)
        t.SAreg = reg
        t.SAloc = loc
    elif isinstance(t, Local):
        if t.thread == None: raise Exception("Threads should be assigned to events and registers before calling encode()")
        ### If the event is active, the value of the register and the expression coincide
        exp = t.exp.encode(localMap)
        reg = Int("T%s_%s%s" %(str(t.thread), str(t.reg), str(getFresh(t.reg, localMap))))
        enc = Implies(Bool(ev(t)), reg == exp)
        t.SAreg = reg
        t.SAexp = exp
    elif isinstance(t, Load):
        if t.thread == None: raise Exception("Threads should be assigned to events and registers before calling encode()")
        ### If the event is active, the value of the register and the location coincide
        loc = t.loc.encode(localMap)
        reg = Int("T%s_%s%s" %(str(t.thread), str(t.reg), str(getFresh(t.reg, localMap))))
        enc = Implies(Bool(ev(t)), reg == loc)
        t.SAreg = reg
        t.SAloc = loc
    elif isinstance(t, Seq):
        if t.thread == None: raise Exception("Threads should be assigned to events and registers before calling encode()")
        ### The data flow of a sequences is the conjuction of the dataflow of its sub-threads
        (enc1, localMap) = encodeDF(t.t1, localMap)
        (enc2, localMap) = encodeDF(t.t2, localMap)
        enc =  And(enc1, enc2)
    elif isinstance(t, If):
        if t.thread == None: raise Exception("Threads should be assigned to events and registers before calling encode()")
        ### If sub-thread t1 is active, then the predicate is true, if t2 is active then the predicate is false
        enc = And(Implies(Bool(repr(t.t1)), t.pred.encode(localMap)), Implies(Bool(repr(t.t2)), Not(t.pred.encode(localMap))))
        ### For the recursive calls we make copies of the map
        indexes1 = copy(localMap)
        (enc1, indexes1) = encodeDF(t.t1, indexes1)
        indexes2 = copy(localMap)
        (enc2, indexes2) = encodeDF(t.t2, indexes2)
        enc = And(enc, enc1, enc2)
        ### We encode any missing variable in some branch
        enc = And(encodeMissingIndexes(t, indexes1, indexes2), enc)
        ### And finally merge the local copies of the maps
        localMap = mergeMaps(indexes1, indexes2)
    elif isinstance(t, Skip):
        if t.thread == None: raise Exception("Threads should be assigned to events and registers before calling encode()")
        ### Skip programs do not contribute to the data flow
        enc = True
    elif isinstance(t, Barrier):
        enc = True
    elif isinstance(t, While): raise Exception("The program should be unrolled before calling to encode")
    else: raise Exception("Type error in encodeDF()")
    return (enc, localMap)

def encodeMissingIndexes(t, indexes1, indexes2):
    ### Returns a constraint that updates the unused variables in some branches of the if thread (x_{i+1} == x_i)
    ### (see for example page 191 of the paper "Exploration of the Capabilities of Constraint Programming")
    new = True
    for k in indexes1.keys():
        k1 = getLast(k, indexes1)
        k2 = getLast(k, indexes2)
        if k1 > k2:
            if isinstance(k, Register):
                index = And(map(lambda i : Int("T%s_%s%s" %(str(t.thread), str(k), str(i+1))) == Int("T%s_%s%s" %(str(t.thread), str(k), str(i))), range(k2, k1)))
            elif isinstance(k, Location):
                index = And(map(lambda i : Int(str(k) + str(i+1)) == Int(str(k) + str(i)), range(k2, k1)))
            else: raise Exception("Type error")
            new = And(Implies(Not(Bool(repr(t.t1))), index), new)
    for k in indexes2.keys():
        k1 = getLast(k, indexes1)
        k2 = getLast(k, indexes2)
        if k2 > k1:
            if isinstance(k, Register):
                index = And(map(lambda i : Int("T%s_%s%s" %(str(t.thread), str(k), str(i+1))) == Int("T%s_%s%s" %(str(t.thread), str(k), str(i))), range(k1, k2)))
            elif isinstance(k, Location):
                index = And(map(lambda i : Int(str(k) + str(i+1)) == Int(str(k) + str(i)), range(k2, k1)))
            else: raise Exception("Type error")
            new = And(Implies(Not(Bool(repr(t.t2))), index), new)
    return new

def mergeMaps(map1, map2):
    """ Returns a new map that merges the two inputs, i.e. for each key it returns the maximal value. """
    ### This is used to update the mapping of an if thread after each sub-thread updated its local copy of the map
    newMap = {}
    for k in map1.keys():
        if k in map2.keys(): newMap[k] = max(map1[k], map2[k])
        else: newMap[k] = map1[k]
    for k in map2.keys():
        if k in map1.keys(): newMap[k] = max(map1[k], map2[k])
        else: newMap[k] = map2[k]
    
    return newMap