from Encoding import *

def RmoConsistent(m):
    events = [e for e in m.events() if isinstance(e, (Load, Store, Init))]
    barriers = [e for e in m.events() if isinstance(e, Barrier)]
    eventsL = [e for e in m.events() if not isinstance(e, Barrier)]
    threads = list(set([e.thread for e in events if not isinstance(e, Init)]))
    
    enc = encodeDomain(events, barriers, eventsL)
    enc = And(enc, encode(m))
    
    ### SC per location
    enc = And(enc, satUnion('ws', 'fr', events))
    enc = And(enc, satUnion('(ws+fr)', 'rf', events, 'com'))
    enc = And(enc, satMinus('poloc', 'RR', events))
    enc = And(enc, satUnion('(poloc\RR)', 'com', events))
    enc = And(enc, satAcyclic('((poloc\RR)+com)', events))
    
    ### RMO
    for t in threads:
        eventsLPerThread = [e for e in eventsL if e.thread == t]
        enc = And(enc, satTransFixPoint('idd', eventsLPerThread))
    enc = And(enc, satIntersection('idd^+', 'RW', events, 'data'))
    enc = And(enc, satEmpty('addr', events))
    enc = And(enc, satUnion('addr', 'data', events, 'ppoW'))
    enc = And(enc, satEq('mfence', 'fenceRmo', events))
    enc = And(enc, satUnion('(ws+fr)', 'rfe', events))
    enc = And(enc, satUnion('((ws+fr)+rfe)', 'fenceRmo', events))
    enc = And(enc, satUnion('(((ws+fr)+rfe)+fenceRmo)', 'ppoW', events, 'ghbW'))
    enc = And(enc, satAcyclic('ghbW', events))
    
    return enc

def RmoInconsistent(m):
    events = [e for e in m.events() if isinstance(e, (Load, Store, Init))]
    eventsL = [e for e in m.events() if not isinstance(e, Barrier)]
    threads = list(set([e.thread for e in events if not isinstance(e, Init)]))
    
    enc = True
    for t in threads:
        eventsLPerThread = [e for e in eventsL if e.thread == t]
        enc = And(enc, satTransFixPoint('idd', eventsLPerThread))
    enc = And(enc, satIntersection('idd^+', 'RW', events, 'data'))
    enc = And(enc, satEmpty('addr', events))
    enc = And(enc, satUnion('addr', 'data', events, 'ppoS'))
    enc = And(enc, satEq('mfence', 'fenceRmo', events))
    enc = And(enc, satUnion('(ws+fr)', 'rfe', events))
    enc = And(enc, satUnion('((ws+fr)+rfe)', 'fenceRmo', events))
    enc = And(enc, satUnion('(((ws+fr)+rfe)+fenceRmo)', 'ppoS', events, 'ghbS'))
    enc = And(enc, satCycle('ghbS', events))
    
    return enc