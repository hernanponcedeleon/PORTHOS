from Encoding import *

def Rmo(m):
    events = [e for e in m.events() if isinstance(e, (Load, Store, Init))]
    eventsL = [e for e in m.events() if not isinstance(e, Barrier)]
    threads = list(set([e.thread for e in events if not isinstance(e, Init)]))
    
    ### All communication relations
    enc = satUnion('ws', 'fr', events)
    enc = And(enc, satUnion('(ws+fr)', 'rf', events, 'com'))
    
    ### Uniproc
    enc = And(enc, satMinus('poloc', 'RR', events))
    enc = And(enc, satUnion('(poloc\RR)', 'com', events))
    
    ### Communication relations for RMO
    enc = And(enc, satUnion('(ws+fr)', 'rfe', events, 'com-rmo'))

    ### Program order for RMO
    for t in threads:
        eventsLPerThread = [e for e in eventsL if e.thread == t]
        enc = And(enc, satTransFixPoint('idd', eventsLPerThread))
    enc = And(enc, satIntersection('idd^+', 'RW', events, 'data'))
    enc = And(enc, satEmpty('addr', events))
    enc = And(enc, satUnion('addr', 'data', events))
    enc = And(enc, satUnion('(addr+data)', 'ctrl', events))
    enc = And(enc, satUnion('((addr+data)+ctrl)', 'sync', events, 'po-rmo'))

    ### Global happens before for TSO
    enc = And(enc, satUnion('po-rmo', 'com-rmo', events, 'ghb-rmo'))

    return enc

def RmoConsistent(m):
    events = [e for e in m.events() if isinstance(e, (Load, Store, Init))]
    
    return And(satAcyclic('((poloc\RR)+com)', events), satAcyclic('ghb-rmo', events))

def RmoInconsistent(m):
    events = [e for e in m.events() if isinstance(e, (Load, Store, Init))]
    
    return Or(satCycle('((poloc\RR)+com)', events), satCycle('ghb-rmo', events))