from Encoding import *

def Tso(m):
    events = [e for e in m.events() if isinstance(e, (Load, Store, Init))]

    ### All communication relations
    enc = satUnion('co', 'fr', events)
    enc = And(enc, satUnion('(co+fr)', 'rf', events, 'com'))

    ### Uniproc
    enc = And(enc, satUnion('poloc', 'com', events))
    
    ### Communication relations for TSO
    enc = And(enc, satUnion('(co+fr)', 'rfe', events, 'com-tso'))

    ### Program order for TSO
    enc = And(enc, satMinus('po', 'WR', events))
    enc = And(enc, satUnion('(po\WR)', 'sync', events, 'po-tso'))

    ### Global happens before for TSO
    enc = And(enc, satUnion('po-tso', 'com-tso', events, 'ghb-tso'))
    
    return enc

def TsoConsistent(m):
    events = [e for e in m.events() if isinstance(e, (Load, Store, Init))]

    return And(satAcyclic('(poloc+com)', events), satAcyclic('ghb-tso', events))

def TsoInconsistent(m):
    events = [e for e in m.events() if isinstance(e, (Load, Store, Init))]
    
    enc = And(satCycleDef('(poloc+com)', events), satCycleDef('ghb-tso', events))
    enc = And(enc, Or(satCycle('(poloc+com)', events), satCycle('ghb-tso', events)))
    return enc