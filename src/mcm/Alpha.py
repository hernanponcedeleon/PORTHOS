from Encoding import *

def AlphaConsistent(m):
    events = [e for e in m.events() if isinstance(e, (Load, Store, Init))]
    barriers = [e for e in m.events() if isinstance(e, Barrier)]
    eventsL = [e for e in m.events() if not isinstance(e, Barrier)]
    threads = list(set([e.thread for e in events if not isinstance(e, Init)]))
    
    enc = encodeDomain(events, barriers, eventsL)
    enc = And(enc, encode(m))
    
    ### SC per location
    enc = And(enc, satUnion('ws', 'fr', events))
    enc = And(enc, satUnion('(ws+fr)', 'rf', events, 'com'))
    enc = And(enc, satUnion('poloc', 'com', events))
    enc = And(enc, satAcyclic('(poloc+com)', events))
    
    ### Thin air
    for t in threads:
        eventsLPerThread = [e for e in eventsL if e.thread == t]
        enc = And(enc, satTransFixPoint('idd', eventsLPerThread))
    enc = And(enc, satIntersection('idd^+', 'RW', events, 'data'))
    enc = And(enc, satUnion('rf', 'data', events))
    enc = And(enc, satAcyclic('(rf+data)', events))
    
    ### Alpha
    enc = And(enc, satUnion('WW', 'RM', events))
    enc = And(enc, satIntersection('(WW+RM)', 'loc', events))
    enc = And(enc, satIntersection('po', '((WW+RM)&loc)', events, 'ppoW'))
    enc = And(enc, satEq('mfence', 'fenceAlpha', events))
    enc = And(enc, satUnion('(ws+fr)', 'rfe', events))
    enc = And(enc, satUnion('((ws+fr)+rfe)', 'fenceAplha', events))
    enc = And(enc, satUnion('(((ws+fr)+rfe)+fenceAlpha)', 'ppoW', events, 'ghbW'))
    enc = And(enc, satAcyclic('ghbW', events))
    
    return enc

def AlphaInconsistent(m):
    events = [e for e in m.events() if isinstance(e, (Load, Store, Init))]
    barriers = [e for e in m.events() if isinstance(e, Barrier)]
    eventsL = [e for e in m.events() if not isinstance(e, Barrier)]
    threads = list(set([e.thread for e in events if not isinstance(e, Init)]))
    
    enc = encodeDomain(events, barriers, eventsL)
    enc = And(enc, encode(m))
    
    ### Thin air
    for t in threads:
        eventsLPerThread = [e for e in eventsL if e.thread == t]
        enc = And(enc, satTransFixPoint('idd', eventsLPerThread))
    enc = And(enc, satIntersection('idd^+', 'RW', events, 'data'))
    enc = And(enc, satUnion('data', 'ctrl', events, 'dp'))
    enc = And(enc, satUnion('rf', 'dp', events))
    enc = And(enc, satAcyclic('(rf+dp)', events))
    
    ### Alpha
    enc = And(enc, satUnion('WW', 'RM', events))
    enc = And(enc, satIntersection('(WW+RM)', 'loc', events))
    enc = And(enc, satIntersection('po', '((WW+RM)&loc)', events, 'ppoS'))
    enc = And(enc, satEq('mfence', 'fenceAlpha', events))
    enc = And(enc, satUnion('(ws+fr)', 'rfe', events))
    enc = And(enc, satUnion('((ws+fr)+rfe)', 'fenceAlpha', events))
    enc = And(enc, satUnion('(((ws+fr)+rfe)+fenceAlpha)', 'ppoS', events, 'ghbS'))
    enc = And(enc, satCycle('ghbS', events))
    
    return enc