from Encoding import *

def CavConsistent(m):
    events = [e for e in m.events() if isinstance(e, (Load, Store, Init))]
    barriers = [e for e in m.events() if isinstance(e, Barrier)]
    eventsL = [e for e in m.events() if not isinstance(e, Barrier)]
    threads = list(set([e.thread for e in events if not isinstance(e, Init)]))
    
    ### PPO for CAV
    enc = True
    for t in threads:
        eventsLPerThread = [e for e in eventsL if e.thread == t]
        enc = And(enc, satTransFixPoint('idd', eventsLPerThread))
        enc = And(enc, satIntersection('idd^+', 'RW', eventsLPerThread, 'data'))
        enc = And(enc, satIntersection('poloc', 'WR', eventsLPerThread))
        enc = And(enc, satUnion('data', '(poloc&WR)', eventsLPerThread))
        enc = And(enc, satTransFixPoint('(data+(poloc&WR))', eventsLPerThread))
        enc = And(enc, satIntersection('(data+(poloc&WR))^+', 'RM', eventsLPerThread))
        enc = And(enc, satUnion('ctrl', 'isync', eventsLPerThread))
        enc = And(enc, satUnion('(ctrl+isync)', '((data+(poloc&WR))^+&RM)', eventsLPerThread, 'ppoW'))
    
    ### Fences for CAV
    enc = And(enc, satFencesCAV(events))
    
    ### SC per location
    enc = And(enc, satUnion('ws', 'fr', events))
    enc = And(enc, satUnion('(ws+fr)', 'rf', events, 'com'))
    enc = And(enc, satUnion('poloc', 'com', events))
    enc = And(enc, satAcyclic('(poloc+com)', events))
    
    ### CAV happens Before
    enc = And(enc, satUnion('(ws+fr)', 'fenceCAV', events))
    enc = And(enc, satUnion('((ws+fr)+fenceCAV)', 'ppoW', events, 'ghbS'))
    enc = And(enc, satAcyclic('ghbW', events))
    
    return enc

def CavInconsistent(m):
    events = [e for e in m.events() if isinstance(e, (Load, Store, Init))]
    barriers = [e for e in m.events() if isinstance(e, Barrier)]
    eventsL = [e for e in m.events() if not isinstance(e, Barrier)]
    threads = list(set([e.thread for e in events if not isinstance(e, Init)]))
    
    ### PPO for CAV
    enc = True
    for t in threads:
        eventsLPerThread = [e for e in eventsL if e.thread == t]
        enc = And(enc, satTransFixPoint('idd', eventsLPerThread))
        enc = And(enc, satIntersection('idd^+', 'RW', eventsLPerThread, 'data'))
        enc = And(enc, satIntersection('poloc', 'WR', eventsLPerThread))
        enc = And(enc, satUnion('data', '(poloc&WR)', eventsLPerThread))
        enc = And(enc, satTransFixPoint('(data+(poloc&WR))', eventsLPerThread))
        enc = And(enc, satIntersection('(data+(poloc&WR))^+', 'RM', eventsLPerThread))
        enc = And(enc, satUnion('ctrl', 'isync', eventsLPerThread))
        enc = And(enc, satUnion('(ctrl+isync)', '((data+(poloc&WR))^+&RM)', eventsLPerThread, 'ppoS'))
    
    ### Fences for CAV
    enc = And(enc, satFencesCAV(events))
    
    ### SC per location
    enc = And(enc, satUnion('ws', 'fr', events))
    enc = And(enc, satUnion('(ws+fr)', 'rf', events, 'com'))
    enc = And(enc, satUnion('poloc', 'com', events))
    enc = And(enc, satAcyclic('(poloc+com)', events))
    
    ### Cycle detection
    enc = And(enc, satUnion('(ws+fr)', 'fenceCAV', events))
    enc = And(enc, satUnion('((ws+fr)+fenceCAV)', 'ppoS', events, 'ghbS'))
    enc = And(enc, satCycle('ghbS', events))
    
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
