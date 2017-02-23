from Encoding import *
from PowerSpe import *

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