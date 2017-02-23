from Encoding import *

def PsoConsistent(m):
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
    
    ### PSO
    enc = And(enc, satIntersection('po', 'RM', events, 'ppoW'))
    enc = And(enc, satEq('mfence', 'fencePso', events))
    enc = And(enc, satUnion('(ws+fr)', 'rfe', events))
    enc = And(enc, satUnion('((ws+fr)+rfe)', 'fencePso', events))
    enc = And(enc, satUnion('(((ws+fr)+rfe)+fencePso)', 'ppoW', events, 'ghbW'))
    enc = And(enc, satAcyclic('ghbW', events))
    
    return enc

def PsoInconsistent(m):
    events = [e for e in m.events() if isinstance(e, (Load, Store, Init))]
    
    enc = satIntersection('po', 'RM', events, 'ppoS')
    enc = And(enc, satEq('mfence', 'fencePso', events))
    enc = And(enc, satUnion('ws', 'fr', events))
    enc = And(enc, satUnion('(ws+fr)', 'rfe', events))
    enc = And(enc, satUnion('((ws+fr)+rfe)', 'fencePso', events))
    enc = And(enc, satUnion('(((ws+fr)+rfe)+fencePso)', 'ppoS', events, 'ghbS'))
    enc = And(enc, satCycle('ghbS', events))
    
    return enc