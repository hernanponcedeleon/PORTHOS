from Encoding import *

def PowerConsistent(m):
    events = [e for e in m.events() if isinstance(e, (Load, Store, Init))]
    barriers = [e for e in m.events() if isinstance(e, Barrier)]
    eventsL = [e for e in m.events() if not isinstance(e, Barrier)]
    
    locs = list(set([e.loc for e in events if not isinstance(e, Barrier)]))
    threads = list(set([e.thread for e in events if not isinstance(e, Init)]))
    
    enc = encodeDomain(events, barriers, eventsL)
    enc = And(enc, encode(m))
    
    for t in threads:
        eventsLPerThread = [e for e in eventsL if e.thread == t]
        enc = And(enc, satTransFixPoint('idd', eventsLPerThread))
    enc = And(enc, satIntersection('idd^+', 'RW', events, 'data'))
    
    ### Fences in Power
    enc = And(enc, satEq('sync', 'ffence', events))
    enc = And(enc, satMinus('lwsync', 'WR', events, 'lwfence'))
    enc = And(enc, satUnion('ffence', 'lwfence', events, 'fencePower'))
    
    ### Some other relations
    enc = And(enc, satEmpty('addr', events))
    enc = And(enc, satUnion('addr', 'data', events, 'dp'))
    for l in locs:
        eventsPerLoc = [e for e in events if e.loc == l]
        enc = And(enc, satCompFreRfe(eventsPerLoc))
        enc = And(enc, satCompWseRfe(eventsPerLoc))
    enc = And(enc, satIntersection('poloc', '(fre;rfe)', events, 'rdw'))
    enc = And(enc, satIntersection('poloc', '(wse;rfe)', events, 'detour'))
    
    ### Base case for the recursion
    enc = And(enc, satUnion('dp', 'rdw', events))
    enc = And(enc, satUnion('(dp+rdw)', 'rfi', events, 'ii0'))
    enc = And(enc, satEmpty('ic0', events))
    enc = And(enc, satUnion('ctrlisync', 'detour', events, 'ci0'))
    enc = And(enc, satUnion('dp', 'poloc', events))
    enc = And(enc, satUnion('(dp+poloc)', 'ctrl', events))
    for t in threads:
        eventsPerThread = [e for e in events if e.thread == t]
        enc = And(enc, satComp('addr', 'po', eventsPerThread))
        ### Recursive
        enc = And(enc, satPowerPPO(eventsPerThread))
    enc = And(enc, satUnion('((dp+poloc)+ctrl)', '(addr;po)', events, 'cc0'))
    
    ### PPO for Power
    enc = And(enc, satIntersection('RR', 'ii', events))
    enc = And(enc, satIntersection('RW', 'ic', events))
    enc = And(enc, satUnion('(RR&ii)', '(RW&ic)', events, 'ppoW'))
    
    ### Thin air check
    enc = And(enc, satUnion('ppoW', 'rfe', events))
    enc = And(enc, satUnion('(ppoW+rfe)', 'fencePower', events, 'hbW'))
    enc = And(enc, satAcyclic('hbW', events))
    
    ### Prop-base
    enc = And(enc, satCompRfeFence(events))
    enc = And(enc, satUnion('fencePower', '(rfe;fencePower)', events))
    enc = And(enc, satTransRef('hbW', events))
    enc = And(enc, satComp('(fencePower+(rfe;fencePower))', '(hbW)*', events, 'prop-base'))
    
    ### Prop for Power
    for l in locs:
        eventsPerLoc = [e for e in events if e.loc == l]
        enc = And(enc, satTransRef('com', eventsPerLoc))
    enc = And(enc, satTransRef('prop-base', events))
    enc = And(enc, satCompComProp(events))
    enc = And(enc, satCompComPropSync(events))
    enc = And(enc, satComp('(((com)*;(prop-base)*);sync)', '(hbW)*', events))
    enc = And(enc, satIntersection('WW', 'prop-base', events))
    enc = And(enc, satUnion('(WW&prop-base)', '((((com)*;(prop-base)*);sync);(hbW)*)', events, 'prop'))
    
    ### Observation check
    enc = And(enc, satCompFreProp(events))
    enc = And(enc, satCompFrePropHb(events))
    enc = And(enc, satIrref('((fre;prop);(hbW)*)', events))
    
    ### Propagation check
    enc = And(enc, satUnion('ws', 'prop', events))
    enc = And(enc, satAcyclic('(ws+prop)', events))
    
    ### SC per location
    enc = And(enc, satUnion('ws', 'fr', events))
    enc = And(enc, satUnion('(ws+fr)', 'rf', events, 'com'))
    enc = And(enc, satUnion('poloc', 'com', events))
    enc = And(enc, satAcyclic('(poloc+com)', events))
    
    return enc

def PowerInconsistent(m):
    events = [e for e in m.events() if isinstance(e, (Load, Store, Init))]
    barriers = [e for e in m.events() if isinstance(e, Barrier)]
    eventsL = [e for e in m.events() if not isinstance(e, Barrier)]
    
    locs = list(set([e.loc for e in events if not isinstance(e, Barrier)]))
    threads = list(set([e.thread for e in events if not isinstance(e, Init)]))
    
    enc = encodeDomain(events, barriers, eventsL)
    enc = And(enc, encode(m))
    
    for t in threads:
        eventsLPerThread = [e for e in eventsL if e.thread == t]
        enc = And(enc, satTransFixPoint('idd', eventsLPerThread))
    enc = And(enc, satIntersection('idd^+', 'RW', events, 'data'))
    
    ### Fences in Power
    enc = And(enc, satUnion('sync', 'ffence', events))
    enc = And(enc, satMinus('lwsync', 'WR', events, 'lwfence'))
    enc = And(enc, satUnion('ffence', 'lwfence', events, 'fencePower'))
    
    ### Some other relations
    enc = And(enc, satEmpty('addr', events))
    enc = And(enc, satUnion('addr', 'data', events, 'dp'))
    for l in locs:
        eventsPerLoc = [e for e in events if e.loc == l]
        enc = And(enc, satCompFreRfe(eventsPerLoc))
        enc = And(enc, satCompWseRfe(eventsPerLoc))
    enc = And(enc, satIntersection('poloc', '(fre;rfe)', events, 'rdw'))
    enc = And(enc, satIntersection('poloc', '(wse;rfe)', events, 'detour'))
    
    ### Base case for the recursion
    enc = And(enc, satUnion('dp', 'rdw', events))
    enc = And(enc, satUnion('(dp+rdw)', 'rfi', events, 'ii0'))
    enc = And(enc, satEmpty('ic0', events))
    enc = And(enc, satUnion('ctrlisync', 'detour', events, 'ci0'))
    enc = And(enc, satUnion('dp', 'poloc', events))
    enc = And(enc, satUnion('(dp+poloc)', 'ctrl', events))
    for t in threads:
        eventsPerThread = [e for e in events if e.thread == t]
        enc = And(enc, satComp('addr', 'po', eventsPerThread))
        ### Recursive
        enc = And(enc, satPowerPPO(eventsPerThread))
    enc = And(enc, satUnion('((dp+poloc)+ctrl)', '(addr;po)', events, 'cc0'))
    
    ### PPO for Power
    enc = And(enc, satIntersection('RR', 'ii', events))
    enc = And(enc, satIntersection('RW', 'ic', events))
    enc = And(enc, satUnion('(RR&ii)', '(RW&ic)', events, 'ppoS'))
    
    ### Thin air check
    enc = And(enc, satUnion('ppoS', 'rfe', events))
    enc = And(enc, satUnion('(ppoS+rfe)', 'fencePower', events, 'hbS'))
    
    ### Prop-base
    enc = And(enc, satCompRfeFence(events))
    enc = And(enc, satUnion('fencePower', '(rfe;fencePower)', events))
    enc = And(enc, satTransRef('hbS', events))
    enc = And(enc, satComp('(fencePower+(rfe;fencePower))', '(hbS)*', events, 'prop-base'))
    
    ### Prop for Power
    for l in locs:
        eventsPerLoc = [e for e in events if e.loc == l]
        enc = And(enc, satTransRef('com', eventsPerLoc))
    enc = And(enc, satTransRef('prop-base', events))
    enc = And(enc, satCompComProp(events))
    enc = And(enc, satCompComPropSync(events))
    enc = And(enc, satComp('(((com)*;(prop-base)*);sync)', '(hbS)*', events))
    enc = And(enc, satIntersection('WW', 'prop-base', events))
    enc = And(enc, satUnion('(WW&prop-base)', '((((com)*;(prop-base)*);sync);(hbS)*)', events, 'prop'))
    
    ### Observation check
    enc = And(enc, satCompFreProp(events))
    enc = And(enc, satCompFrePropHb(events))
    
    ### Propagation check
    enc = And(enc, satUnion('ws', 'prop', events))
    
    ### SC per location
    enc = And(enc, satUnion('ws', 'fr', events))
    enc = And(enc, satUnion('(ws+fr)', 'rf', events, 'com'))
    enc = And(enc, satUnion('poloc', 'com', events))
    
    ### Axiom violation
    enc = And(enc, Or(satCycle('hbS', events), satCycle('(ws+prop)', events), satCycle('(poloc+com)', events), satRef('((fre;prop);(hbS)*)', events)))
    
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