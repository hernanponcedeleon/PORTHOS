from Encoding import *

def TsoConsistent(m):
    events = [e for e in m.events() if isinstance(e, (Load, Store, Init))]

    enc = encodeDomain(m)
    enc = And(enc, encode(m))
    
    ### SC per location
    enc = And(enc, satUnion('ws', 'fr', events))
    enc = And(enc, satUnion('(ws+fr)', 'rf', events, 'com'))
    enc = And(enc, satUnion('poloc', 'com', events))
    enc = And(enc, satAcyclic('(poloc+com)', events))
    
    ### TSO
    enc = And(enc, satMinus('po', 'WR', events))
    enc = And(enc, satUnion('(po\WR)', 'sync', events, 'po-tso'))
    enc = And(enc, satUnion('(ws+fr)', 'rfe', events, 'com-tso'))
    enc = And(enc, satUnion('po-tso', 'com-tso', events, 'ghb-tso'))
    enc = And(enc, satAcyclic('ghb-tso', events))
    
    return enc

def TsoInconsistent(m):
    events = [e for e in m.events() if isinstance(e, (Load, Store, Init))]
    
    enc = satMinus('po', 'WR', events)
    enc = And(enc, satUnion('(po\WR)', 'sync', events, 'po-tso'))
    enc = And(enc, satUnion('(ws+fr)', 'rfe', events, 'com-tso'))
    enc = And(enc, satUnion('po-tso', 'com-tso', events, 'ghb-tso'))
    enc = And(enc, satCycle('ghb-tso', events))

    return enc