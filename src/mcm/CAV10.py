from Encoding import *

def Cav(m):
    events = [e for e in m.events() if isinstance(e, (Load, Store, Init))]
    eventsL = [e for e in m.events() if not isinstance(e, Barrier)]
    threads = list(set([e.thread for e in events if not isinstance(e, Init)]))

    ### Uniproc
    enc = satUnion('co', 'fr', events)
    enc = And(enc, satUnion('(co+fr)', 'rf', events, 'com'))
    enc = And(enc, satUnion('poloc', 'com', events))

    ### dp for CAV
    for t in threads:
        eventsLPerThread = [e for e in eventsL if e.thread == t]
        enc = And(enc, satTransFixPoint('idd', eventsLPerThread))
        enc = And(enc, satIntersection('idd^+', 'RW', eventsLPerThread, 'data'))
    enc = And(enc, satIntersection('poloc', 'WR', events))
    enc = And(enc, satUnion('data', '(poloc&WR)', events))
    enc = And(enc, satTransFixPoint('(data+(poloc&WR))', events))
    enc = And(enc, satIntersection('(data+(poloc&WR))^+', 'RM', events))
    enc = And(enc, satIntersection('ctrl', 'RW', events))
    enc = And(enc, satUnion('(ctrl&RW)', 'ctrlisync', events))
    ### We don't support address dependencies yet
    enc = And(enc, satUnion('((ctrl&RW)+ctrlisync)', '((data+(poloc&WR))^+&RM)', events, 'dp-cav'))

    ### Thin-air
    enc = And(enc, satUnion('dp-cav', 'rf', events))

    ### Fences for CAV
    enc = And(enc, satCavFences(events))

    ### Program order for CAV
    enc = And(enc, satUnion('dp-cav', 'fence-cav', events, 'po-cav'))

    ### CAV happens Before
    enc = And(enc, satUnion('(co+fr)', 'po-cav', events, 'hb-cav'))
    
    return enc

def CavConsistent(m):
    events = [e for e in m.events() if isinstance(e, (Load, Store, Init))]

    return And(satAcyclic('(poloc+com)', events), satAcyclic('(dp-cav+rf)'), satAcyclic('hb-cav', events))

def CavInconsistent(m):
    events = [e for e in m.events() if isinstance(e, (Load, Store, Init))]

    return Or(satACycle('(poloc+com)', events), satCycle('(dp-cav+rf)'), satCycle('hb-cav', events))


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
        enc = And(enc, Implies(edge('(rf;ablwsync)',e1,e2), orClause3))
        enc = And(enc, Implies(orClause3, edge('(rf;ablwsync)',e1,e2)))
        enc = And(enc, Implies(edge('(ablwsync;rf)',e1,e2), orClause4))
        enc = And(enc, Implies(orClause4, edge('(ablwsync;rf)',e1,e2)))
        
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
                                                                                                            
        enc = And(enc, satUnion('absync', 'ablwsync', events, 'fence-cav'))
    
    return enc
