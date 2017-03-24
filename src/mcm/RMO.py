from Encoding import *

def Rmo(m):
    events = [e for e in m.events() if isinstance(e, (Load, Store, Init))]
    eventsL = [e for e in m.events() if not isinstance(e, Barrier)]
    threads = list(set([e.thread for e in events if not isinstance(e, Init)]))
    
    ### All communication relations
    enc = satUnion('co', 'fr', events)
    enc = And(enc, satUnion('(co+fr)', 'rf', events, 'com'))
    
    ### Uniproc
    enc = And(enc, satMinus('poloc', 'RR', events))
    enc = And(enc, satUnion('(poloc\RR)', 'com', events))
    
    ### Communication relations for RMO
    enc = And(enc, satUnion('(co+fr)', 'rfe', events, 'com-rmo'))

    ### Program order for RMO
    for t in threads:
        eventsLPerThread = [e for e in eventsL if e.thread == t]
        enc = And(enc, satTransFixPoint('idd', eventsLPerThread))
        enc = And(enc, satIntersection('idd^+', 'RW', eventsLPerThread, 'data'))
    enc = And(enc, satIntersection('poloc', 'WR', events))
    enc = And(enc, satUnion('data', '(poloc&WR)', events))
    enc = And(enc, satTransFixPoint('(data+(poloc&WR))', events))
    enc = And(enc, satIntersection('(data+(poloc&WR))^+', 'RM', events))
    enc = And(enc, satIntersection('ctrl', 'RW', events))
    enc = And(enc, satUnion('(ctrl&RW)', 'ctrlisync', events))
    ### We don't support address dependencies yet
    enc = And(enc, satUnion('((ctrl&RW)+ctrlisync)', '((data+(poloc&WR))^+&RM)', events, 'dp-rmo'))
    enc = And(enc, satUnion('dp-rmo', 'sync', events, 'po-rmo'))

    ### Global happens before for RMO
    enc = And(enc, satUnion('po-rmo', 'com-rmo', events, 'ghb-rmo'))

    return enc

def RmoConsistent(m):
    events = [e for e in m.events() if isinstance(e, (Load, Store, Init))]
    
    return And(satAcyclic('((poloc\RR)+com)', events), satAcyclic('ghb-rmo', events))

def RmoInconsistent(m):
    events = [e for e in m.events() if isinstance(e, (Load, Store, Init))]
    
    enc = And(satCycleDef('((poloc\RR)+com)', events), satCycleDef('ghb-rmo', events))
    enc = And(enc, Or(satCycle('((poloc\RR)+com)', events), satCycle('ghb-rmo', events)))
    return enc