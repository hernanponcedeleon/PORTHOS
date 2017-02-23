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

def satCompComProp(events):
    enc = True
    for e1, e2 in product (events, events):
        if not isinstance(e1, (Load, Init, Store)): continue
        orClause = Or([And(edge('(com)*',e1,e3), edge('(prop-base)*',e3,e2)) for e3 in events if isinstance(e3, (Load, Init, Store)) and e1.loc == e3.loc])
        enc = And(enc, Implies(edge('((com)*;(prop-base)*)',e1,e2), orClause))
        enc= And(enc, Implies(orClause, edge('((com)*;(prop-base)*)',e1,e2)))
    return enc

def satCompComPropSync(events):
    enc = True
    for e1, e2 in product (events, events):
        if not isinstance(e1, (Load, Init, Store)): continue
        orClause = Or([And(edge('((com)*;(prop-base)*)',e1,e3), edge('sync',e3,e2)) for e3 in events if e2.thread == e3.thread])
        enc = And(enc, Implies(edge('(((com)*;(prop-base)*);sync)',e1,e2), orClause))
        enc= And(enc, Implies(orClause, edge('(((com)*;(prop-base)*);sync)',e1,e2)))
    return enc

def satCompFreProp(events):
    enc = True
    for e1, e2 in product (events, events):
        if not isinstance(e1, Load): continue
        orClause = Or([And(edge('fre',e1,e3), edge('prop',e3,e2)) for e3 in events if isinstance(e3, Store) and e1.thread != e3.thread and e1.loc == e3.loc])
        enc = And(enc, Implies(edge('(fre;prop)',e1,e2), orClause))
        enc= And(enc, Implies(orClause, edge('(fre;prop)',e1,e2)))
    return enc

def satCompFrePropHb(events):
    enc = True
    for e1, e2 in product (events, events):
        if not isinstance(e1, Load): continue
        orClause = Or([And(edge('(fre;prop)',e1,e3), edge('(hbW)*',e3,e2)) for e3 in events])
        enc = And(enc, Implies(edge('((fre;prop);(hbW)*)',e1,e2), orClause))
        enc= And(enc, Implies(orClause, edge('((fre;prop);(hbW)*)',e1,e2)))
    return enc

def satCompRfeFence(events):
    enc = True
    for e1, e2 in product (events, events):
        if not isinstance(e1, (Init, Store)): continue
        orClause = Or([And(edge('rfe',e1,e3), edge('fencePower',e3,e2)) for e3 in events if isinstance(e3, Load) and e1.thread != e3.thread and e2.thread == e3.thread])
        enc = And(enc, Implies(edge('(rfe;fencePower)',e1,e2), orClause))
        enc= And(enc, Implies(orClause, edge('(rfe;fencePower)',e1,e2)))
    return enc

def satCompFreRfe(events):
    enc = True
    for e1, e2 in product (events, events):
        if not isinstance(e1, Load) or not isinstance(e1, Load): continue
        orClause = Or([And(edge('fre',e1,e3), edge('rfe',e3,e2)) for e3 in events if isinstance(e3, (Init, Store)) and e1.thread != e3.thread and e2.thread != e3.thread and e1.loc == e3.loc and e2.loc == e3.loc])
        enc = And(enc, Implies(edge('(fre;rfe)',e1,e2), orClause))
        enc= And(enc, Implies(orClause, edge('(fre;fre)',e1,e2)))
    return enc

def satCompWseRfe(events):
    enc = True
    for e1, e2 in product (events, events):
        if not isinstance(e1, (Init, Store)) or not isinstance(e1, Load): continue
        orClause = Or([And(edge('wse',e1,e3), edge('rfe',e3,e2)) for e3 in events if isinstance(e3, (Init, Store)) and e1.thread != e3.thread and e2.thread != e3.thread and e1.loc == e3.loc and e2.loc == e3.loc])
        enc = And(enc, Implies(edge('(wse;rfe)',e1,e2), orClause))
        enc= And(enc, Implies(orClause, edge('(wse;fre)',e1,e2)))
    return enc