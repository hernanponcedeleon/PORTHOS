from Encoding import *

def Alpha(m):
    events = [e for e in m.events() if isinstance(e, (Load, Store, Init))]
    eventsL = [e for e in m.events() if not isinstance(e, Barrier)]
    threads = list(set([e.thread for e in events if not isinstance(e, Init)]))
    
    ### All communication relations
    enc = satUnion('ws', 'fr', events)
    enc = And(enc, satUnion('(ws+fr)', 'rf', events, 'com'))

    ### Uniproc
    enc = And(enc, satUnion('poloc', 'com', events))

    ### Communication relations for Alpha
    enc = And(enc, satUnion('(ws+fr)', 'rfe', events, 'com-alpha'))

    ### Thin air
    for t in threads:
        eventsLPerThread = [e for e in eventsL if e.thread == t]
        enc = And(enc, satTransFixPoint('idd', eventsLPerThread))
    enc = And(enc, satIntersection('idd^+', 'RW', events, 'data'))
    enc = And(enc, satEmpty('addr', events))
    enc = And(enc, satUnion('addr', 'data', events))
    enc = And(enc, satUnion('(addr+data)', 'ctrl', events, 'dp-alpha'))
    enc = And(enc, satUnion('rf', 'dp-alpha', events))
    #    enc = And(enc, satAcyclic('(rf+data)', events))
    
    ### Alpha
    enc = And(enc, satUnion('WW', 'RM', events))
    enc = And(enc, satIntersection('(WW+RM)', 'loc', events))
    enc = And(enc, satIntersection('po', '((WW+RM)&loc)', events))
    enc = And(enc, satUnion('(po&((WW+RM)&loc))', 'sync', events, 'po-apha'))

    return enc

def AlphaConsistent(m):
    events = [e for e in m.events() if isinstance(e, (Load, Store, Init))]
    
    return And(satAcyclic('(rf+data)', events), satAcyclic('(poloc+com)', events), satAcyclic('ghb-rmo', events))

def AlphaInconsistent(m):
    events = [e for e in m.events() if isinstance(e, (Load, Store, Init))]
    
    return Or(satCycle('(rf+data)', events), satCycle('(poloc+com)', events), satCycle('ghb-rmo', events))