from Encoding import *

def Alpha(m):
    events = [e for e in m.events() if isinstance(e, (Load, Store, Init))]
    eventsL = [e for e in m.events() if not isinstance(e, Barrier)]
    threads = list(set([e.thread for e in events if not isinstance(e, Init)]))
    
    ### Uniproc
    enc = satUnion('co', 'fr', events)
    enc = And(enc, satUnion('(co+fr)', 'rf', events, 'com'))
    enc = And(enc, satUnion('poloc', 'com', events))

    ### Communication relations for Alpha
    enc = And(enc, satUnion('(co+fr)', 'rfe', events, 'com-alpha'))

    ### dp for Alpha
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
    enc = And(enc, satUnion('((ctrl&RW)+ctrlisync)', '((data+(poloc&WR))^+&RM)', events, 'dp-alpha'))

    ### Thin-air
    enc = And(enc, satUnion('dp-alpha', 'rf', events))

    ### Program order for Alpha
    enc = And(enc, satUnion('WW', 'RM', events))
    enc = And(enc, satIntersection('(WW+RM)', 'loc', events))
    enc = And(enc, satIntersection('po', '((WW+RM)&loc)', events))
    enc = And(enc, satUnion('(po&((WW+RM)&loc))', 'sync', events, 'po-alpha'))

    ### Global happens before for Alpha
    enc = And(enc, satUnion('po-alpha', 'com-alpha', events, 'ghb-alpha'))

    return enc

def AlphaConsistent(m):
    events = [e for e in m.events() if isinstance(e, (Load, Store, Init))]
    
    return And(satAcyclic('(poloc+com)', events), satAcyclic('(dp-alpha+rf)', events), satAcyclic('ghb-alpha', events))

def AlphaInconsistent(m):
    events = [e for e in m.events() if isinstance(e, (Load, Store, Init))]
    
    enc = And(satCycleDef('(poloc+com)', events), satCycleDef('(dp-alpha+rf)', events), satCycleDef('ghb-tso', events))
    enc = And(enc, Or(satCycle('(poloc+com)', events), satCycle('(dp-alpha+rf)', events), satCycle('ghb-tso', events)))
    return enc