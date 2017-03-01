from Program import *
from itertools import product
from math import log

def intVar(name, e): return Int('%s(%s)' %(name, ev(e)))

def intCount(rel, e1, e2): return Int('%s(%s,%s)' %(rel, ev(e1), ev(e2)))

def encodeDomain(events, barriers, eventsL):
    enc = True
    t1 = time()

    for e1, e2 in product(eventsL, eventsL):
        if e1 == e2:
            enc = And(enc, Not(edge('ii',e1,e2)))
            enc = And(enc, Not(edge('ic',e1,e2)))
            enc = And(enc, Not(edge('ci',e1,e2)))
            enc = And(enc, Not(edge('cc',e1,e2)))

    for e1, e2 in product(events, events):
        for rel in ['ws', 'rf', 'fr', 'apo', 'fence', 'data']:
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
                ##if e1.condLevel < e2.condLevel and isinstance(e1, (Local, Load, Init, Store)) and isinstance(e2, (Local, Load, Init, Store)) and e1.reg in e2.condReg:
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
            enc = And(enc, Not(edge('ws',e1,e2)))
        if not (isinstance(e1, Load) and isinstance(e2, (Store, Init)) and e1.loc == e2.loc):
            enc = And(enc, Not(edge('fr',e1,e2)))
        if not (e1.thread == e2.thread and e1.pid < e2.pid):
            enc = And(enc, Not(edge('fence',e1,e2)))
            enc = And(enc, Not(edge('fenceCAV',e1,e2)))

        enc = And(enc, Implies(edge('fencePower',e1,e2), edge('fence',e1,e2)))
        enc = And(enc, Implies(edge('fenceTso',e1,e2), edge('fence',e1,e2)))
        enc = And(enc, Implies(edge('fencePso',e1,e2), edge('fence',e1,e2)))
        enc = And(enc, Implies(edge('fenceRmo',e1,e2), edge('fence',e1,e2)))
        enc = And(enc, Implies(edge('fenceAlpha',e1,e2), edge('fence',e1,e2)))
#        enc = And(enc, Implies(edge('mfence',e1,e2), edge('fence',e1,e2)))
#        enc = And(enc, Implies(edge('ffence',e1,e2), edge('fence',e1,e2)))
#        enc = And(enc, Implies(edge('lwfence',e1,e2), edge('fence',e1,e2)))
        enc = And(enc, Implies(edge('rf',e1,e2), Or(edge('rfe',e1,e2), edge('rfi',e1,e2))))
        enc = And(enc, Implies(edge('rfe',e1,e2), And(edge('rf',e1,e2), edge('ext',e1,e2))))
        enc = And(enc, Implies(edge('rfi',e1,e2), And(edge('rf',e1,e2), edge('int',e1,e2))))
        enc = And(enc, Implies(edge('ws',e1,e2), Or(edge('wse',e1,e2), edge('wsi',e1,e2))))
        enc = And(enc, Implies(edge('wse',e1,e2), And(edge('ws',e1,e2), edge('ext',e1,e2))))
        enc = And(enc, Implies(edge('wsi',e1,e2), And(edge('ws',e1,e2), edge('int',e1,e2))))
        enc = And(enc, Implies(edge('fr',e1,e2), Or(edge('fre',e1,e2), edge('fri',e1,e2))))
        enc = And(enc, Implies(edge('fre',e1,e2), And(edge('fr',e1,e2), edge('ext',e1,e2))))
        enc = And(enc, Implies(edge('fri',e1,e2), And(edge('fr',e1,e2), edge('int',e1,e2))))
        ### PO: order imposed by the order of instructions
        ### PPO: subset of PO guaranteed to be preserbed by the memory model
        ### APO: actual order performed by the memory model; should satisfy PPO
        enc = And(enc, Implies(edge('ppoW',e1,e2), edge('po',e1,e2)))
        enc = And(enc, Implies(edge('ppoW',e1,e2), edge('apoW',e1,e2)))
        enc = And(enc, Implies(edge('ppoS',e1,e2), edge('po',e1,e2)))
        enc = And(enc, Implies(edge('ppoS',e1,e2), edge('apoS',e1,e2)))
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
#        if isinstance(e2, Mfence) and e1.thread == e2.thread and e2.thread == e3.thread and e1.pid < e2.pid and e2.pid < e3.pid:
#            enc = And(enc, Implies(And([Bool(ev(e1)), Bool(ev(e2)), Bool(ev(e3))]), edge('mfence',e1,e3)))
        if isinstance(e2, Sync) and e1.thread == e2.thread and e2.thread == e3.thread and e1.pid < e2.pid and e2.pid < e3.pid:
            enc = And(enc, Implies(And([Bool(ev(e1)), Bool(ev(e2)), Bool(ev(e3))]), edge('sync',e1,e3)))
        if isinstance(e2, Lwsync) and e1.thread == e2.thread and e2.thread == e3.thread and e1.pid < e2.pid and e2.pid < e3.pid:
            enc = And(enc, Implies(And([Bool(ev(e1)), Bool(ev(e2)), Bool(ev(e3))]), edge('lwsync',e1,e3)))
        ### Check!
        if isinstance(e2, Isync) and e1.thread == e2.thread and e2.thread == e3.thread and e1.pid < e2.pid and e2.pid < e3.pid:
            enc = And(enc, Implies(And([Bool(ev(e1)), Bool(ev(e2)), Bool(ev(e3))]), edge('isync',e1,e3)))


    for e1, e2 in product(events, events):
        if e1.thread != e2.thread: continue
        nofence = True
        for e3 in barriers:
            if e3.thread != e1.thread: continue
            if e1.pid < e3.pid and e3.pid < e2.pid: nofence = False
        if nofence:
            enc = And(enc, Not(edge('fence',e1,e2)))
            enc = And(enc, Not(edge('fenceCAV',e1,e2)))
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
#        nomfence = True
#        for e3 in [e for e in barriers if isinstance(e, Mfence)]:
#            if e3.thread != e1.thread: continue
#            if e1.pid < e3.pid and e3.pid < e2.pid: nomfence = False
#        if nomfence:
#            enc = And(enc, Not(edge('mfence',e1,e2)))

    for e1, e2 in product(eventsL, eventsL):
        if e1.thread != e2.thread or e2.pid < e1.pid or e1 == e2:
            enc = And(enc, Not(edge('idd',e1,e2)))
#            enc = And(enc, Not(edge('idd^+',e1,e2)))
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

    ### FR is defined in terms of WS and RF
    for e1 in events:
        for e2, e3 in product(events, events):
                enc = And(enc, Implies(And(edge('rf', e3, e1), edge('ws', e3, e2)), edge('fr', e1, e2)))

    for l in locs:
        ### WS is a total order per location
        writeEventsLoc = [e for e in events if isinstance(e, (Store, Init)) and e.loc == l]
        enc = And(enc, satTO('ws', writeEventsLoc))

    ### Init events are the first one in the WS total order
    enc = And(enc, And([intVar('ws', e) == 1 for e in events if isinstance(e, Init)]))

    ### each Load RF exactly one write event
    for e in filter(lambda e: isinstance(e, Load), events):
        pairs = map(lambda w: edge('rf',w,e), events)
        enc = And(enc, Implies(Bool(ev(e)), encodeEO(pairs)))

    for t in threads:
        eventsThread = filter(lambda e: e.thread == t, events)
        enc = And(enc, satTO('apoW', eventsThread))
        enc = And(enc, satTO('apoS', eventsThread))

    #print "\tDom: %.2f" %(time() - t1)
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

def satFencesCAV(events):
    enc = True
    
    for e1, e2 in product(events, events):
        orClause1 = Or([And(edge('rf',e1,e3), edge('absync',e3,e2)) for e3 in events])
        orClause2 = Or([And(edge('absync',e1,e3), edge('rf',e3,e2)) for e3 in events])
        orClause3 = Or([And(edge('rf',e1,e3), edge('ablwsync',e3,e2)) for e3 in events])
        orClause4 = Or([And(edge('ablwsync',e1,e3), edge('rf',e3,e2)) for e3 in events])

        enc = And(enc, Implies(edge('rf;absync',e1,e2), orClause1))
        enc = And(enc, Implies(orClause1, edge('rf;absync',e1,e2)))
        enc = And(enc, Implies(edge('absync;rf',e1,e2), orClause2))
        enc = And(enc, Implies(orClause2, edge('absync;rf',e1,e2)))
        enc = And(enc, Implies(edge('rf;ablwsync',e1,e2), orClause3))
        enc = And(enc, Implies(orClause3, edge('rf;ablwsync',e1,e2)))
        enc = And(enc, Implies(edge('ablwsync;rf',e1,e2), orClause4))
        enc = And(enc, Implies(orClause4, edge('ablwsync;rf',e1,e2)))

        enc = And(enc, Implies(edge('absync',e1,e2), Or([edge('sync',e1,e2), edge('rf;absync',e1,e2), edge('absync;rf',e1,e2)])))
        enc = And(enc, Implies(Or([edge('sync',e1,e2), edge('rf;absync',e1,e2), edge('absync;rf',e1,e2)]), edge('absync',e1,e2)))
        enc = And(enc, Implies(edge('ablwsync',e1,e2), Or([edge('lwfence',e1,e2), edge('rf;ablwsync',e1,e2), edge('ablwsync;rf',e1,e2)])))
        enc = And(enc, Implies(Or([edge('lwfence',e1,e2), edge('rf;ablwsync',e1,e2), edge('ablwsync;rf',e1,e2)]), edge('ablwsync',e1,e2)))

        enc = And(enc, Implies(edge('absync',e1,e2), Or([And(edge('sync',e1,e2), intCount('absync',e1,e2) > intCount('sync',e1,e2)),
                                                     And(edge('rf;absync',e1,e2), intCount('absync',e1,e2) > intCount('rf;absync',e1,e2)),
                                                     And(edge('absync;rf',e1,e2), intCount('absync',e1,e2) > intCount('absync;rf',e1,e2)),])))
        enc = And(enc, Implies(edge('ablwsync',e1,e2), Or([And(edge('lwfence',e1,e2), intCount('ablwsync',e1,e2) > intCount('lwfence',e1,e2)),
                                                     And(edge('rf;ablwsync',e1,e2), intCount('ablwsync',e1,e2) > intCount('rf;ablwsync',e1,e2)),
                                                     And(edge('ablwsync;rf',e1,e2), intCount('ablwsync',e1,e2) > intCount('ablwsync;rf',e1,e2)),])))

    enc = And(enc, satUnion('absync', 'ablwsync', events, 'fence'))
    return enc    

def satPowerPPO(events):
    t1 = time()
    enc = True

    for e1, e2 in product(events, events):
        orClause1 = Or([And(edge('ic',e1,e3), edge('ci',e3,e2)) for e3 in events])
        orClause2 = Or([And(edge('ii',e1,e3), edge('ii',e3,e2)) for e3 in events])
        orClause3 = Or([And(edge('ic',e1,e3), edge('cc',e3,e2)) for e3 in events])
        orClause4 = Or([And(edge('ii',e1,e3), edge('ic',e3,e2)) for e3 in events])
        orClause5 = Or([And(edge('ci',e1,e3), edge('ii',e3,e2)) for e3 in events])
        orClause6 = Or([And(edge('cc',e1,e3), edge('ci',e3,e2)) for e3 in events])
        orClause7 = Or([And(edge('ci',e1,e3), edge('ic',e3,e2)) for e3 in events])
        orClause8 = Or([And(edge('cc',e1,e3), edge('cc',e3,e2)) for e3 in events])
        enc = And(enc, Implies(edge('ic;ci',e1,e2), orClause1))
        enc = And(enc, Implies(orClause1, edge('ic;ci',e1,e2)))
        enc = And(enc, Implies(edge('ii;ii',e1,e2), orClause2))
        enc = And(enc, Implies(orClause2, edge('ii;ii',e1,e2)))
        enc = And(enc, Implies(edge('ic;cc',e1,e2), orClause3))
        enc = And(enc, Implies(orClause3, edge('ic;cc',e1,e2)))
        enc = And(enc, Implies(edge('ii;ic',e1,e2), orClause4))
        enc = And(enc, Implies(orClause4, edge('ii;ic',e1,e2)))
        enc = And(enc, Implies(edge('ci;ii',e1,e2), orClause5))
        enc = And(enc, Implies(orClause5, edge('cc;ii',e1,e2)))
        enc = And(enc, Implies(edge('cc;ci',e1,e2), orClause6))
        enc = And(enc, Implies(orClause6, edge('cc;ci',e1,e2)))
        enc = And(enc, Implies(edge('ci;ic',e1,e2), orClause7))
        enc = And(enc, Implies(orClause7, edge('ci;ic',e1,e2)))
        enc = And(enc, Implies(edge('cc;cc',e1,e2), orClause8))
        enc = And(enc, Implies(orClause8, edge('cc;cc',e1,e2)))

        enc = And(enc, Implies(edge('ii',e1,e2), Or([edge('ii0',e1,e2), edge('ci',e1,e2), edge('ic;ci',e1,e2), edge('ii;ii',e1,e2)])))
        enc = And(enc, Implies(Or([edge('ii0',e1,e2), edge('ci',e1,e2), edge('ic;ci',e1,e2), edge('ii;ii',e1,e2)]), edge('ii',e1,e2)))

        enc = And(enc, Implies(edge('ic',e1,e2), Or([edge('ic0',e1,e2), edge('ii',e1,e2), edge('cc',e1,e2), edge('ic;cc',e1,e2), edge('ii;ic',e1,e2)])))
        enc = And(enc, Implies(Or([edge('ic0',e1,e2), edge('ii',e1,e2), edge('cc',e1,e2), edge('ic;cc',e1,e2), edge('ii;ic',e1,e2)]), edge('ic',e1,e2)))

        enc = And(enc, Implies(edge('ci',e1,e2), Or([edge('ci0',e1,e2), edge('ci;ii',e1,e2), edge('cc;ci',e1,e2)])))
        enc = And(enc, Implies(Or([edge('ci0',e1,e2), edge('ci;ii',e1,e2), edge('cc;ci',e1,e2)]), edge('ci',e1,e2)))

        enc = And(enc, Implies(edge('cc',e1,e2), Or([edge('cc0',e1,e2), edge('ci',e1,e2), edge('ci;ic',e1,e2), edge('cc;cc',e1,e2)])))
        enc = And(enc, Implies(Or([edge('cc0',e1,e2), edge('ci',e1,e2), edge('ci;ic',e1,e2), edge('cc;cc',e1,e2)]), edge('cc',e1,e2)))

        enc = And(enc, Implies(edge('ii',e1,e2), Or([And(edge('ii0',e1,e2), intCount('ii',e1,e2) > intCount('ii0',e1,e2)), 
                                                     And(edge('ci',e1,e2), intCount('ii',e1,e2) > intCount('ci',e1,e2)),
                                                     And(edge('ic;ci',e1,e2), intCount('ii',e1,e2) > intCount('ic;ci',e1,e2)),
                                                     And(edge('ii;ii',e1,e2), intCount('ii',e1,e2) > intCount('ii;ii',e1,e2)),])))

        enc = And(enc, Implies(edge('ic',e1,e2), Or([And(edge('ic0',e1,e2), intCount('ic',e1,e2) > intCount('ic0',e1,e2)),
                                                     And(edge('ii',e1,e2), intCount('ic',e1,e2) > intCount('ii',e1,e2)),
                                                     And(edge('cc',e1,e2), intCount('ic',e1,e2) > intCount('cc',e1,e2)),
                                                     And(edge('ic;cc',e1,e2), intCount('ic',e1,e2) > intCount('ic;cc',e1,e2)),
                                                     And(edge('ii;ic',e1,e2), intCount('ic',e1,e2) > intCount('ii;ic',e1,e2)),])))

        enc = And(enc, Implies(edge('ci',e1,e2), Or([And(edge('ci0',e1,e2), intCount('ci',e1,e2) > intCount('ci0',e1,e2)),
                                                     And(edge('ci;ii',e1,e2), intCount('ci',e1,e2) > intCount('ci;ii',e1,e2)),
                                                     And(edge('cc;ci',e1,e2), intCount('ci',e1,e2) > intCount('cc;ci',e1,e2)),])))


        enc = And(enc, Implies(edge('cc',e1,e2), Or([And(edge('cc0',e1,e2), intCount('cc',e1,e2) > intCount('cc0',e1,e2)),
                                                     And(edge('ci',e1,e2), intCount('cc',e1,e2) > intCount('ci',e1,e2)),
                                                     And(edge('ci;ic',e1,e2), intCount('cc',e1,e2) > intCount('ci;ic',e1,e2)),
                                                     And(edge('cc;cc',e1,e2), intCount('cc',e1,e2) > intCount('cc;cc',e1,e2)),])))
       

    #print "\tRec: %.2f" %(time() - t1)
    return enc

def satCavFences(events):
    enc = True

    for e1 , e2 in product(events, events):
        orClause1 = Or([And(edge('rf',e1,e3), edge('absync',e3,e2)) for e3 in events])
        orClause2 = Or([And(edge('absync',e1,e3), edge('rf',e3,e2)) for e3 in events])
        orClause3 = Or([And(edge('rf',e1,e3), edge('ablwsync',e3,e2)) for e3 in events])
        orClause4 = Or([And(edge('ablwsync',e1,e3), edge('rf',e3,e2)) for e3 in events])
        enc = And(enc, Implies(edge('(rf;absync)',e1,e2), orClause1))
        enc = And(enc, Implies(orClause1, edge('(rf;absync)',e1,e2)))
        enc = And(enc, Implies(edge('(absync;rf)',e1,e2), orClause2))
        enc = And(enc, Implies(orClause2, edge('(absync;rf)',e1,e2)))
        enc = And(enc, Implies(edge('(ablwsync;rf)',e1,e2), orClause3))
        enc = And(enc, Implies(orClause3, edge('(ablwsync;rf)',e1,e2)))
        enc = And(enc, Implies(edge('(rf;ablwsync)',e1,e2), orClause4))
        enc = And(enc, Implies(orClause4, edge('(rf;ablwsync)',e1,e2)))

        enc = And(enc, Implies(edge('absync',e1,e2), Or([edge('sync',e1,e2), edge('(rf;absync)',e1,e2), edge('(absync;rf)',e1,e2)])))
        enc = And(enc, Implies(Or([edge('sync',e1,e2), edge('(rf;absync)',e1,e2), edge('(absync;rf)',e1,e2)]), edge('absync',e1,e2)))

        enc = And(enc, satIntersection('RM', 'lwsync', events))
        enc = And(enc, satIntersection('WW', 'lwsync', events))
        enc = And(enc, satIntersection('MW', '(rf;ablwsync)', events))
        enc = And(enc, satIntersection('RM', '(ablwsync;rf)', events))
        enc = And(enc, Implies(edge('ablwsync',e1,e2), Or([edge('(RM&lwsync)',e1,e2), edge('(WW&lwsync)',e1,e2), edge('(MW&(rf;ablwsync))',e1,e2), edge('(RM&(ablwsync;rf))',e1,e2)])))
        enc = And(enc, Implies(Or([edge('(RM&lwsync)',e1,e2), edge('(WW&lwsync)',e1,e2), edge('(MW&(rf;ablwsync))',e1,e2), edge('(RM&(ablwsync;rf))',e1,e2)]), edge('ablwsync',e1,e2)))

        enc = And(enc, Implies(edge('absync',e1,e2), Or([And(edge('sync',e1,e2), intCount('absync',e1,e2) > intCount('sync',e1,e2)),
                                                     And(edge('(rf;absync)',e1,e2), intCount('absync',e1,e2) > intCount('(rf;absync)',e1,e2)),
                                                     And(edge('(absync;rf)',e1,e2), intCount('absync',e1,e2) > intCount('(absync;rf)',e1,e2)),])))

        enc = And(enc, Implies(edge('ablwsync',e1,e2), Or([And(edge('(RM&lwsync)',e1,e2), intCount('ablwsync',e1,e2) > intCount('(RM&lwsync)',e1,e2)),
                                                     And(edge('(WW&lwsync)',e1,e2), intCount('ablwsync',e1,e2) > intCount('(WW&lwsync)',e1,e2)),
                                                     And(edge('(MW&(rf;ablwsync))',e1,e2), intCount('ablwsync',e1,e2) > intCount('(MW&(rf;ablwsync))',e1,e2)),
                                                     And(edge('(RM&(ablwsync;rf))',e1,e2), intCount('ablwsync',e1,e2) > intCount('(RM&(ablwsync;rf))',e1,e2)),])))

        enc = And(enc, satUnion('absync', 'ablwsync', events, 'fenceCAV'))

    return enc

def satTransFixPoint(rel, events):
    enc = True
    for e1,e2 in product(events, events):
        if e1 == e2: enc = And(enc, edge('%s0' %rel,e1,e2))
        else:
            enc = And(enc, Implies(edge('%s0' %rel,e1,e2), edge(rel,e1,e2)))
            enc = And(enc, Implies(edge(rel,e1,e2), edge('%s0' %rel,e1,e2)))

    for i in range(int(log(len(events), 2)) + 1):
        for e1, e2 in product(events, events):
            orClause = False
            for e3 in events:
                orClause = Or(orClause, And(edge('%s%s' %(rel,i),e1,e3), edge('%s%s' %(rel,i),e3,e2)))
            enc = And(enc, Implies(edge('%s%s' %(rel,i+1),e1,e2), orClause))
            enc = And(enc, Implies(orClause, edge('%s%s' %(rel,i+1),e1,e2)))

    for e1, e2 in product(events, events):
        enc = And(enc, edge('%s_plus' %rel,e1,e2) == edge('%s%s' %(rel,int(log(len(events), 2)) + 1),e1,e2))
        if e1 == e2:
            enc = And(enc, Not(edge('%s^+',e1,e2)))
        else:
            enc = And(enc, edge('%s^+' %rel,e1,e2) == edge('%s_plus' %rel,e1,e2))
    return enc

def satTrans(rel, events):
    t1 = time()
    enc = True
    for e1, e2 in product(events, events):
        enc = And(enc, Implies(edge(rel,e1,e2), edge('%s^+' %rel,e1,e2)))
        orClause = Or([And(edge('%s^+' %rel,e1,e3), edge('%s^+' %rel,e3,e2)) for e3 in events])
        enc = And(enc, Implies(orClause, edge('%s^+' %rel,e1,e2))) 
        enc = And(enc, Implies(edge('%s^+' %rel,e1,e2), orClause))
    return enc

def satTransRef(rel, events):
    t1 = time()
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
    t1 = time()
    enc = True
    for e1,e2 in product(events, events):
        if e1 == e2: enc = And(enc, edge('%s0' %rel,e1,e2))
        else:
            enc = And(enc, Implies(edge('%s0' %rel,e1,e2), edge(rel,e1,e2)))
            enc = And(enc, Implies(edge(rel,e1,e2), edge('%s0' %rel,e1,e2)))

    for i in range(int(log(len(events), 2)) + 1):
        for e1, e2 in product(events, events):
            orClause = False
            for e3 in events:
                orClause = Or(orClause, And(edge('%s%s' %(rel,i),e1,e3), edge('%s%s' %(rel,i),e3,e2)))
            enc = And(enc, Implies(edge('%s%s' %(rel,i+1),e1,e2), orClause))
            enc = And(enc, Implies(orClause, edge('%s%s' %(rel,i+1),e1,e2)))

    for e1, e2 in product(events, events):
        enc = And(enc, edge('(%s)*' %rel,e1,e2) == edge('%s%s' %(rel,int(log(len(events), 2)) + 1),e1,e2))
    return enc

def stringTransRef(rel, events, f):
    s = []
    events = eventes[:5]
    for e in events:
        if not edge('(%s)*' %rel,e,e) in s:
            s.append('(declare-fun |%s| () Bool)\n' %edge('(%s)*' %rel,e,e))
        s.append('(assert (= |%s| true))\n' %edge('(%s)*' %rel,e,e))
    for e1, e2 in product(events, events):
        if not edge(rel,e1,e2) in s:
            s.append('(declare-fun |%s| () Bool)\n' %edge(rel,e1,e2))
        if not edge('(%s)*' %rel,e1,e2) in s:
            s.append('(declare-fun |%s| () Bool)\n' %edge('(%s)*' %rel,e1,e2))
        s.append('(assert (=> |%s| |%s|))\n' %(edge(rel,e1,e2), edge('(%s)*' %rel,e1,e2)))
        orClause = 'false'
        for e3 in events:
            if not edge('(%s)*' %rel,e1,e3) in s:
                s.append('(declare-fun |%s| () Bool)\n' %edge('(%s)*' %rel,e1,e3))
            if not str(edge('(%s)*' %rel,e3,e2)) in s:
                s.append('(declare-fun |%s| () Bool)\n' %edge('(%s)*' %rel,e3,e2))
            orClause += '(or %s %s)' %(orClause, '(and |%s| |%s|)' %(edge('(%s)*' %rel,e1,e3), edge('(%s)*' %rel,e3,e2)))
        s.append('(assert (=> |%s| (%s)))\n' %(edge('(%s)*' %rel,e1,e2), orClause))
        s.append('(assert (=> (%s) |%s|))\n' %(orClause, edge('(%s)*' %rel,e1,e2)))
    f.write(''.join(s))
    f.close()
    return

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
    t1 = time()
    if name == None: name = '(%s;%s)' %(rel1, rel2)
    enc = True
    for e1, e2 in product (events, events):
        orClause = Or([And(edge(rel1,e1,e3), edge(rel2,e3,e2)) for e3 in events])
        enc = And(enc, Implies(edge(name,e1,e2), orClause))
        enc= And(enc, Implies(orClause, edge(name,e1,e2)))
    return enc

def satComp2(rel1, rel2, dom, ran, mid, name=None):
    t1 = time()
    if name == None: name = '(%s;%s)' %(rel1, rel2)
    enc = True
    for e1, e2 in product (dom, ran):
        orClause = Or([And(edge(rel1,e1,e3), edge(rel2,e3,e2)) for e3 in mid])
        enc = And(enc, Implies(edge(name,e1,e2), orClause))
        enc= And(enc, Implies(orClause, edge(name,e1,e2)))
    return enc

def satCompComProp(events):
    t1 = time()
    enc = True
    for e1, e2 in product (events, events):
        if not isinstance(e1, (Load, Init, Store)): continue
        orClause = Or([And(edge('(com)*',e1,e3), edge('(prop-base)*',e3,e2)) for e3 in events if isinstance(e3, (Load, Init, Store)) and e1.loc == e3.loc])
        enc = And(enc, Implies(edge('((com)*;(prop-base)*)',e1,e2), orClause))
        enc= And(enc, Implies(orClause, edge('((com)*;(prop-base)*)',e1,e2)))
    return enc

def satCompComPropSync(events):
    t1 = time()
    enc = True
    for e1, e2 in product (events, events):
        if not isinstance(e1, (Load, Init, Store)): continue
        orClause = Or([And(edge('((com)*;(prop-base)*)',e1,e3), edge('sync',e3,e2)) for e3 in events if e2.thread == e3.thread])
        enc = And(enc, Implies(edge('(((com)*;(prop-base)*);sync)',e1,e2), orClause))
        enc= And(enc, Implies(orClause, edge('(((com)*;(prop-base)*);sync)',e1,e2)))
    return enc

def satCompFreProp(events):
    t1 = time()
    enc = True
    for e1, e2 in product (events, events):
        if not isinstance(e1, Load): continue
        orClause = Or([And(edge('fre',e1,e3), edge('prop',e3,e2)) for e3 in events if isinstance(e3, Store) and e1.thread != e3.thread and e1.loc == e3.loc])
        enc = And(enc, Implies(edge('(fre;prop)',e1,e2), orClause))
        enc= And(enc, Implies(orClause, edge('(fre;prop)',e1,e2)))
    return enc

def satCompFrePropHb(events):
    t1 = time()
    enc = True
    for e1, e2 in product (events, events):
        if not isinstance(e1, Load): continue
        orClause = Or([And(edge('(fre;prop)',e1,e3), edge('(hbW)*',e3,e2)) for e3 in events])
        enc = And(enc, Implies(edge('((fre;prop);(hbW)*)',e1,e2), orClause))
        enc= And(enc, Implies(orClause, edge('((fre;prop);(hbW)*)',e1,e2)))
    return enc

def satCompRfeFence(events):
    t1 = time()
    enc = True
    for e1, e2 in product (events, events):
        if not isinstance(e1, (Init, Store)): continue
        orClause = Or([And(edge('rfe',e1,e3), edge('fencePower',e3,e2)) for e3 in events if isinstance(e3, Load) and e1.thread != e3.thread and e2.thread == e3.thread])
        enc = And(enc, Implies(edge('(rfe;fencePower)',e1,e2), orClause))
        enc= And(enc, Implies(orClause, edge('(rfe;fencePower)',e1,e2)))
    return enc

def satCompFreRfe(events):
    t1 = time()
    enc = True
    for e1, e2 in product (events, events):
        if not isinstance(e1, Load) or not isinstance(e1, Load): continue
        orClause = Or([And(edge('fre',e1,e3), edge('rfe',e3,e2)) for e3 in events if isinstance(e3, (Init, Store)) and e1.thread != e3.thread and e2.thread != e3.thread and e1.loc == e3.loc and e2.loc == e3.loc])
        enc = And(enc, Implies(edge('(fre;rfe)',e1,e2), orClause))
        enc= And(enc, Implies(orClause, edge('(fre;fre)',e1,e2)))
    return enc

def satCompWseRfe(events):
    t1 = time()
    enc = True
    for e1, e2 in product (events, events):
        if not isinstance(e1, (Init, Store)) or not isinstance(e1, Load): continue
        orClause = Or([And(edge('wse',e1,e3), edge('rfe',e3,e2)) for e3 in events if isinstance(e3, (Init, Store)) and e1.thread != e3.thread and e2.thread != e3.thread and e1.loc == e3.loc and e2.loc == e3.loc])
        enc = And(enc, Implies(edge('(wse;rfe)',e1,e2), orClause))
        enc= And(enc, Implies(orClause, edge('(wse;fre)',e1,e2)))
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
