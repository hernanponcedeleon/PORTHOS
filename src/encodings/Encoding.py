from Program import *
from itertools import product
from math import log

def encodeDomain(m):
    events = [e for e in m.events() if isinstance(e, (Load, Store, Init))]
    barriers = [e for e in m.events() if isinstance(e, Barrier)]
    eventsL = [e for e in m.events() if not isinstance(e, Barrier)]
    enc = True

    for e1, e2 in product(eventsL, eventsL):
        if e1 == e2:
            enc = And(enc, Not(edge('ii',e1,e2)))
            enc = And(enc, Not(edge('ic',e1,e2)))
            enc = And(enc, Not(edge('ci',e1,e2)))
            enc = And(enc, Not(edge('cc',e1,e2)))

    for e1, e2 in product(events, events):
        for rel in ['co', 'rf', 'fr']:
            enc = And(enc, Implies(edge(rel, e1, e2), And(Bool(ev(e1)), Bool(ev(e2)))))
        if not isinstance(e1, Init):
            enc = And(enc, Not(edge('IM',e1,e2)))
            enc = And(enc, Not(edge('IW',e1,e2)))
            enc = And(enc, Not(edge('IR',e1,e2)))
        else:
            enc = And(enc, edge('IM',e1,e2))
        if not isinstance(e2, Init):
            enc = And(enc, Not(edge('MI',e1,e2)))
            enc = And(enc, Not(edge('WI',e1,e2)))
            enc = And(enc, Not(edge('RI',e1,e2)))
        else:
            enc = And(enc, edge('MI',e1,e2))
        if not isinstance(e1, Load):
            enc = And(enc, Not(edge('RM',e1,e2)))
            enc = And(enc, Not(edge('RW',e1,e2)))
            enc = And(enc, Not(edge('RR',e1,e2)))
        else:
            enc = And(enc, edge('RM',e1,e2))
        if not isinstance(e2, Load):
            enc = And(enc, Not(edge('MR',e1,e2)))
            enc = And(enc, Not(edge('WR',e1,e2)))
            enc = And(enc, Not(edge('RR',e1,e2)))
        else:
            enc = And(enc, edge('MR',e1,e2))
        if not isinstance(e1, (Store, Init)):
            enc = And(enc, Not(edge('WM',e1,e2)))
            enc = And(enc, Not(edge('WW',e1,e2)))
            enc = And(enc, Not(edge('WR',e1,e2)))
        else:
            enc = And(enc, edge('WM',e1,e2))
        if not isinstance(e2, (Store, Init)):
            enc = And(enc, Not(edge('MW',e1,e2)))
            enc = And(enc, Not(edge('WW',e1,e2)))
            enc = And(enc, Not(edge('RW',e1,e2)))
        else:
            enc = And(enc, edge('MW',e1,e2))
        if isinstance(e1, Load) and isinstance(e2, Load):
            enc = And(enc, edge('RR',e1,e2))
        if isinstance(e1, Load) and isinstance(e2, (Init, Store)):
            enc = And(enc, edge('RW',e1,e2))
        if isinstance(e1, (Init, Store)) and isinstance(e2, (Init, Store)):
            enc = And(enc, edge('WW',e1,e2))
        if isinstance(e1, (Init, Store)) and isinstance(e2, Load):
            enc = And(enc, edge('WR',e1,e2))

        if e1 == e2:
            enc = And(enc, edge('id',e1,e2))
            enc = And(enc, Not(edge('ii',e1,e2)))
            enc = And(enc, Not(edge('ic',e1,e2)))
            enc = And(enc, Not(edge('ci',e1,e2)))
            enc = And(enc, Not(edge('cc',e1,e2)))
        else:
            enc = And(enc, Not(edge('id',e1,e2)))

        if e1.thread == e2.thread:
            enc = And(enc, edge('int',e1,e2))
            enc = And(enc, Not(edge('ext',e1,e2)))
            if e1.pid < e2.pid:
                enc = And(enc, edge('po',e1,e2))
                ## CTRL can only originate on a read
                if e1.condLevel < e2.condLevel and isinstance(e1, Load) and isinstance(e2, (Local, Load, Init, Store)) and e1.reg in e2.condReg:
                    enc = And(enc, edge('ctrl',e1,e2))
                else:
                    enc = And(enc, Not(edge('ctrl',e1,e2)))
            else:
                enc = And(enc, Not(edge('po',e1,e2)))
                enc = And(enc, Not(edge('ctrl',e1,e2)))
            if not(isinstance(e1, Load) and isinstance(e2, Store) and e1.pid < e2.pid):
                enc = And(enc, Not(edge('data',e1,e2)))
            if not isinstance(e1, Init) and isinstance(e2, Store) and e1.pid == (e2.pid - 1):
                lastMod = e2.getMapLastMod()[e2.reg]
                if e1.reg not in lastMod:
                    enc = And(enc, Not(edge('idd^+',e1,e2)))
            if not isinstance(e1, Init) and isinstance(e2, Local) and e1.pid == (e2.pid - 1):
                found = False
                for r in getRegs(e2.exp):
                    lastMod = e.getMapLastMod()[r]
                    if e1.reg in lastMod: found = True
                if not found:
                    enc = And(enc, Not(edge('idd^+',e1,e2)))
        else:
            enc = And(enc, Not(edge('int',e1,e2)))
            enc = And(enc, edge('ext',e1,e2))
            enc = And(enc, Not(edge('po',e1,e2)))
            enc = And(enc, Not(edge('data',e1,e2)))
            enc = And(enc, Not(edge('ctrl',e1,e2)))
        if e1.loc == e2.loc:
            enc = And(enc, edge('loc',e1,e2))
        else:
            enc = And(enc, Not(edge('loc',e1,e2)))
        if not (isinstance(e1, (Store, Init)) and isinstance(e2, Load) and e1.loc == e2.loc):
            enc = And(enc, Not(edge('rf',e1,e2)))
        if not (isinstance(e1, (Store, Init)) and isinstance(e2, (Store, Init)) and e1.loc == e2.loc):
            enc = And(enc, Not(edge('co',e1,e2)))
        if not (isinstance(e1, Load) and isinstance(e2, (Store, Init)) and e1.loc == e2.loc):
            enc = And(enc, Not(edge('fr',e1,e2)))
        if not (e1.thread == e2.thread and e1.pid < e2.pid):
            enc = And(enc, Not(edge('sync',e1,e2)))
            enc = And(enc, Not(edge('lwsync',e1,e2)))
            enc = And(enc, Not(edge('isync',e1,e2)))

        enc = And(enc, Implies(edge('rf',e1,e2), Or(edge('rfe',e1,e2), edge('rfi',e1,e2))))
        enc = And(enc, Implies(edge('rfe',e1,e2), And(edge('rf',e1,e2), edge('ext',e1,e2))))
        enc = And(enc, Implies(edge('rfi',e1,e2), And(edge('rf',e1,e2), edge('int',e1,e2))))
        enc = And(enc, Implies(edge('co',e1,e2), Or(edge('coe',e1,e2), edge('coi',e1,e2))))
        enc = And(enc, Implies(edge('coe',e1,e2), And(edge('co',e1,e2), edge('ext',e1,e2))))
        enc = And(enc, Implies(edge('coi',e1,e2), And(edge('co',e1,e2), edge('int',e1,e2))))
        enc = And(enc, Implies(edge('fr',e1,e2), Or(edge('fre',e1,e2), edge('fri',e1,e2))))
        enc = And(enc, Implies(edge('fre',e1,e2), And(edge('fr',e1,e2), edge('ext',e1,e2))))
        enc = And(enc, Implies(edge('fri',e1,e2), And(edge('fr',e1,e2), edge('int',e1,e2))))
        ### PO: order imposed by the order of instructions
        ### PPO: subset of PO guaranteed to be preserbed by the memory model
        ### APO: actual order performed by the memory model; should satisfy PPO
        enc = And(enc, Implies(edge('poloc',e1,e2), And(edge('po',e1,e2), edge('loc',e1,e2))))
        enc = And(enc, Implies(And(edge('po',e1,e2), edge('loc',e1,e2)), edge('poloc',e1,e2)))
        enc = And(enc, Implies(And(edge('(idd^+&RW)',e1,e2), And(Bool(ev(e1)), Bool(ev(e2)))), edge('data',e1,e2)))
        enc = And(enc, Implies(edge('data',e1,e2), edge('(idd^+&RW)',e1,e2)))
        enc = And(enc, Implies(And(edge('ctrl',e1,e2), edge('isync',e1,e2)), edge('ctrlisync',e1,e2)))
        enc = And(enc, Implies(edge('ctrlisync',e1,e2), And(edge('ctrl',e1,e2), edge('isync',e1,e2))))

    locs = set([x.loc for x in filter(lambda e: not isinstance(e, Barrier), events)])
    threads = set(x.thread for x in filter(lambda e: not isinstance(e, Init), events))

    eventsB = events + barriers

    for e1, e2, e3 in product(eventsB, eventsB, eventsB):
        if isinstance(e2, Sync) and e1.thread == e2.thread and e2.thread == e3.thread and e1.pid < e2.pid and e2.pid < e3.pid:
            enc = And(enc, Implies(And([Bool(ev(e1)), Bool(ev(e2)), Bool(ev(e3))]), edge('sync',e1,e3)))
        if isinstance(e2, Lwsync) and e1.thread == e2.thread and e2.thread == e3.thread and e1.pid < e2.pid and e2.pid < e3.pid:
            enc = And(enc, Implies(And([Bool(ev(e1)), Bool(ev(e2)), Bool(ev(e3))]), edge('lwsync',e1,e3)))
        if isinstance(e2, Isync) and e1.thread == e2.thread and e2.thread == e3.thread and e1.pid < e2.pid and e2.pid < e3.pid:
            enc = And(enc, Implies(And([Bool(ev(e1)), Bool(ev(e2)), Bool(ev(e3))]), edge('isync',e1,e3)))

    for e1, e2 in product(events, events):
        if e1.thread != e2.thread: continue
        nosync = True
        for e3 in [e for e in barriers if isinstance(e, Sync)]:
            if e3.thread != e1.thread: continue
            if e1.pid < e3.pid and e3.pid < e2.pid: nosync = False
        if nosync:
            enc = And(enc, Not(edge('sync',e1,e2)))
        noisync = True
        for e3 in [e for e in barriers if isinstance(e, Isync)]:
            if e3.thread != e1.thread: continue
            if e1.pid < e3.pid and e3.pid < e2.pid: noisync = False
        if noisync:
            enc = And(enc, Not(edge('isync',e1,e2)))
        nolwsync = True
        for e3 in [e for e in barriers if isinstance(e, Lwsync)]:
            if e3.thread != e1.thread: continue
            if e1.pid < e3.pid and e3.pid < e2.pid: nolwsync = False
        if nolwsync:
            enc = And(enc, Not(edge('lwsync',e1,e2)))

    for e1, e2 in product(eventsL, eventsL):
        if e1.thread != e2.thread or e2.pid < e1.pid or e1 == e2:
            enc = And(enc, Not(edge('idd',e1,e2)))
        if isinstance(e2, Store):
            lastMod = e2.getMapLastMod()[e2.reg]
            if not e1 in lastMod:
                enc = And(enc, Not(edge('idd',e1,e2)))
        elif isinstance(e2, Load):
            if not e2.loc in e2.getMapLastMod().keys():
                enc = And(enc, Not(edge('idd',e1,e2)))
        elif isinstance(e2, Local) and isinstance(e2.exp, int):
            enc = And(enc, Not(edge('idd',e1,e2)))

    for e in eventsL:
        if isinstance(e, Store):
            lastMod = e.getMapLastMod()[e.reg]
            enc = And(enc, Or(map(lambda x: edge('idd',x,e), lastMod)))
        elif isinstance(e, Load):
            if not e.loc in e.getMapLastMod().keys(): continue
            lastMod = e.getMapLastMod()[e.loc]
            enc = And(enc, Or(map(lambda x: edge('idd',x,e), lastMod)))
        elif isinstance(e, Local):
            for r in getRegs(e.exp):
                lastMod = e.getMapLastMod()[r]
                enc = And(enc, Or(map(lambda x: edge('idd',x,e), lastMod)))

    ### FR is defined in terms of CO and RF
    for e1 in events:
        for e2, e3 in product(events, events):
                enc = And(enc, Implies(And(edge('rf', e3, e1), edge('co', e3, e2)), edge('fr', e1, e2)))

    for l in locs:
        ### CO is a total order per location
        writeEventsLoc = [e for e in events if isinstance(e, (Store, Init)) and e.loc == l]
        enc = And(enc, satTO('co', writeEventsLoc))

    ### Init events are the first one in the CO total order
    enc = And(enc, And([intVar('co', e) == 1 for e in events if isinstance(e, Init)]))

    ### each Load RF exactly one write event
    for e in filter(lambda e: isinstance(e, Load), events):
        pairs = map(lambda w: edge('rf',w,e), events)
        enc = And(enc, Implies(Bool(ev(e)), encodeEO(pairs)))

    return enc

def satEmpty(rel, events):
    enc = True
    for e1, e2 in product(events, events):
        enc = And(enc, Not(edge(rel,e1,e2)))
    return enc

def satCycle(rel, events):
    enc = True
    for e1 in events:
        source, target = [], []
        for e2 in events:
            source.append(cycleEdge(rel,e1,e2))
            target.append(cycleEdge(rel,e2,e1))
            enc = And(enc, Implies(cycleEdge(rel,e1,e2), edge(rel,e1,e2)))
            enc = And(enc, Implies(cycleEdge(rel,e1,e2), And(cycleVar(e1), cycleVar(e2))))
        enc = And(enc, Implies(cycleVar(e1), encodeALO(source)))
        enc = And(enc, Implies(cycleVar(e1),encodeALO(target)))
    enc = And(enc, Or([cycleVar(e) for e in events]))
    return enc

def satTransFixPoint(rel, events):
    enc = True
    for e1,e2 in product(events, events):
        enc = And(enc, edge('%s0' %rel,e1,e2) == edge(rel,e1,e2))
        enc = And(enc, edge('%s^+' %rel,e1,e2) == edge('%s%s' %(rel,int(log(len(events), 2)) + 1),e1,e2))

    for i in range(int(log(len(events), 2)) + 1):
        for e1, e2 in product(events, events):
            orClause = False
            for e3 in events:
                orClause = Or(orClause, And(edge('%s%s' %(rel,i),e1,e3), edge('%s%s' %(rel,i),e3,e2)))
            enc = And(enc, edge('%s%s' %(rel,i+1),e1,e2) == Or(edge(rel,e1,e2), orClause))
    return enc

def satTrans(rel, events):
    enc = True
    for e1, e2 in product(events, events):
        enc = And(enc, Implies(edge(rel,e1,e2), edge('%s^+' %rel,e1,e2)))
        orClause = Or([And(edge('%s^+' %rel,e1,e3), edge('%s^+' %rel,e3,e2)) for e3 in events])
        enc = And(enc, Implies(orClause, edge('%s^+' %rel,e1,e2))) 
        enc = And(enc, Implies(edge('%s^+' %rel,e1,e2), orClause))
    return enc

def satTransRef(rel, events):
    enc = True
    for e in events:
        enc = And(enc, edge('(%s)*' %rel,e,e))
    for e1, e2 in product(events, events):
        enc = And(enc, Implies(edge(rel,e1,e2), edge('(%s)*' %rel,e1,e2)))
        orClause = Or([And(edge('(%s)*' %rel,e1,e3), edge('(%s)*' %rel,e3,e2)) for e3 in events])
        enc = And(enc, Implies(orClause, edge('(%s)*' %rel,e1,e2)))
        enc = And(enc, Implies(edge('(%s)*' %rel,e1,e2), orClause))
    return enc

def satTransRefFixPoint(rel, events):
    enc = True
    enc = True
    for e1,e2 in product(events, events):
        enc = And(enc, edge('%s0' %rel,e1,e2) == edge(rel,e1,e2))
        enc = And(enc, edge('%s^+' %rel,e1,e2) == edge('%s%s' %(rel,int(log(len(events), 2)) + 1),e1,e2))
        enc = And(enc, edge('(%s)*' %rel,e1,e2) == Or(edge('%s^+' %rel,e1,e2), edge('id' %rel,e1,e2)))
    
    for i in range(int(log(len(events), 2)) + 1):
        for e1, e2 in product(events, events):
            orClause = False
            for e3 in events:
                orClause = Or(orClause, And(edge('%s%s' %(rel,i),e1,e3), edge('%s%s' %(rel,i),e3,e2)))
            enc = And(enc, edge('%s%s' %(rel,i+1),e1,e2) == Or(edge(rel,e1,e2), orClause))
    return enc

def satIrref(rel, events):
    enc = True
    for e in events:
        enc = And(enc, Not(edge(rel,e,e)))
    return enc

def satRef(rel, events):
    enc = False
    for e in events:
        enc = Or(enc, edge(rel,e,e))
    return enc

def satEq(r1, r2, events):
    enc = True
    for e1, e2 in product(events, events):
        enc = And(enc, Implies(edge(r1,e1,e2), edge(r2,e1,e2)))
        enc = And(enc, Implies(edge(r2,e1,e2), edge(r1,e1,e2)))
    return enc

def satUnion(r1, r2, events, name=None):
    if name == None: name = '(%s+%s)' %(r1, r2)
    enc = True
    for e1, e2 in product(events, events):
        enc = And(enc, Implies(edge(name,e1,e2), Or(edge(r1,e1,e2), edge(r2,e1,e2))))
        enc = And(enc, Implies(Or(edge(r1,e1,e2), edge(r2,e1,e2)), edge(name,e1,e2)))
    return enc

def satIntersection(r1, r2, events, name=None):
    if name == None: name = '(%s&%s)' %(r1, r2)
    enc = True
    for e1, e2 in product(events, events):
        enc = And(enc, Implies(edge(name,e1,e2), And(edge(r1,e1,e2), edge(r2,e1,e2))))
        enc = And(enc, Implies(And(edge(r1,e1,e2), edge(r2,e1,e2)), edge(name,e1,e2)))
    return enc

def satMinus(r1, r2, events, name=None):
    if name == None: name = '(%s\%s)' %(r1, r2)
    enc = True
    for e1, e2 in product(events, events):
        enc = And(enc, Implies(edge(name,e1,e2), And(edge(r1,e1,e2), Not(edge(r2,e1,e2)))))
        enc = And(enc, Implies(And(edge(r1,e1,e2), Not(edge(r2,e1,e2))), edge(name,e1,e2)))
    return enc

def satAcyclic(relName, events):
    enc = True
    for e1, e2 in product(events, events):
        enc = And(enc, Implies(Bool(ev(e1)), intVar(relName, e1) > 0))
        enc = And(enc, Implies(edge(relName,e1,e2), intVar(relName, e1) < intVar(relName, e2)))
    return enc

def satTO(relName, events):
    enc = True
    for e1, e2 in product(events, events):
        enc = And(enc, Implies(Bool(ev(e1)), intVar(relName, e1) > 0))
        enc = And(enc, Implies(Bool(ev(e1)), intVar(relName, e1) <= len(events)))
        enc = And(enc, Implies(edge(relName,e1,e2), intVar(relName, e1) < intVar(relName, e2)))
        enc = And(enc, Implies(And(Bool(ev(e1)), Bool(ev(e2))), Implies(intVar(relName, e1) < intVar(relName, e2), edge(relName,e1,e2))))
        if e1 != e2:
            enc = And(enc, Implies(And(Bool(ev(e1)), Bool(ev(e2))), intVar(relName, e1) != intVar(relName, e2)))
            enc = And(enc, Implies(And(Bool(ev(e1)), Bool(ev(e2))), Or(edge(relName,e1,e2), edge(relName,e2,e1))))
    return enc

def satComp(rel1, rel2, events, name=None):
    if name == None: name = '(%s;%s)' %(rel1, rel2)
    enc = True
    for e1, e2 in product (events, events):
        orClause = Or([And(edge(rel1,e1,e3), edge(rel2,e3,e2)) for e3 in events])
        enc = And(enc, Implies(edge(name,e1,e2), orClause))
        enc= And(enc, Implies(orClause, edge(name,e1,e2)))
    return enc

def satInverse(rel, events):
    enc = True
    for e1, e2 in product(events, events):
        enc = And(enc, Implies(edge(rel,e1,e2), edge('(%s)^-1' %rel,e2,e1)))
        enc = And(enc, Implies(edge('(%s)^-1' %rel,e2,e1), edge(rel,e1,e2)))
    return enc

def satFRInit(events):
    enc = True
    for e1, e2 in product(events, events):
        if not isinstance(e2, Init) or not isinstance(e1, Load) or e1.loc != e2.loc:
            enc = And(enc, Not(edge('frinit',e1,e2)))
        else:
            enc = And(enc, Implies(edge('fr',e1,e2), edge('frinit',e1,e2)))
    return enc

def satDomRanIncl(r1, r2, events):
    enc = True
    for e1 in events:
        orClause1 = Or([edge(r1,e1,e2) for e2 in events])
        orClause2 = Or([edge(r2,e2,e1) for e2 in events])
        enc = And(enc, Implies(orClause1, orClause2))
    return enc
   
def satRefClos(r, events):
    enc = True
    for e in events:
        enc = And(enc, edge('(%s)?' %r,e,e))
    for e1, e2 in product(events, events):
        enc = And(enc, Implies(edge(r,e1,e2), edge('(%s)?' %r,e1,e2)))
        enc = And(enc, Implies(edge('(%s)?' %r,e1,e2), Or(edge(r,e1,e2), edge('id',e1,e2))))
    return enc

def satIncl(r1, r2, events):
    enc = True
    for e1, e2 in product (events, events):
        enc = And(enc, Implies(edge(r1,e1,e2), edge(r2,e1,e2)))
    return enc

def satEmpty(r, events):
    return And([Not(edge(r,e1,e2)) for e1 in events for e2 in events])

def satImm(r, events):
    enc = satComp(r, r, events)
    enc = And(enc, satMinus(r, '(%s;%s)' %(r,r), events, 'imm(%s)' %r))
    return enc
