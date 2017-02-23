from Encoding import *

def TsoConsistent(m):
    events = [e for e in m.events() if isinstance(e, (Load, Store, Init))]
    barriers = [e for e in m.events() if isinstance(e, Barrier)]
    eventsL = [e for e in m.events() if not isinstance(e, Barrier)]
    
    enc = encodeDomain(events, barriers, eventsL)
    enc = And(enc, encode(m))
    
    ### SC per location
    enc = And(enc, satUnion('ws', 'fr', events))
    enc = And(enc, satUnion('(ws+fr)', 'rf', events, 'com'))
    enc = And(enc, satUnion('poloc', 'com', events))
    enc = And(enc, satAcyclic('(poloc+com)', events))
    
    ### TSO
    enc = And(enc, satMinus('po', 'WR', events, 'ppoW'))
    #enc = And(enc, satEq('mfence', 'fenceTso', events))
    enc = And(enc, satUnion('mfence', 'sync', events))
    enc = And(enc, satUnion('(mfence+sync)', 'lwsync', events,'fenceTso'))
    enc = And(enc, satUnion('(ws+fr)', 'rfe', events))
    enc = And(enc, satUnion('((ws+fr)+rfe)', 'fenceTso', events))
    enc = And(enc, satUnion('(((ws+fr)+rfe)+fenceTso)', 'ppoW', events, 'ghbW'))
    enc = And(enc, satAcyclic('ghbW', events))
    
    return enc

def TsoInconsistent(m):
    events = [e for e in m.events() if isinstance(e, (Load, Store, Init))]
    
    enc = satMinus('po', 'WR', events, 'ppoS')
    #enc = And(enc, satEq('mfence', 'fenceTso', events))
    enc = And(enc, satUnion('mfence', 'sync', events))
    enc = And(enc, satUnion('(mfence+sync)', 'lwsync', events, 'fenceTso'))
    enc = And(enc, satUnion('ws', 'fr', events))
    enc = And(enc, satUnion('(ws+fr)', 'rfe', events))
    enc = And(enc, satUnion('((ws+fr)+rfe)', 'fenceTso', events))
    enc = And(enc, satUnion('(((ws+fr)+rfe)+fenceTso)', 'ppoS', events, 'ghbS'))
    enc = And(enc, satCycle('ghbS', events))
    
    return enc