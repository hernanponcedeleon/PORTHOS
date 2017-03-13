from Encoding import *

def Pso(m):
    events = [e for e in m.events() if isinstance(e, (Load, Store, Init))]
    
    ### All communication relations
    enc = satUnion('ws', 'fr', events)
    enc = And(enc, satUnion('(ws+fr)', 'rf', events, 'com'))
    
    ### Uniproc
    enc = And(enc, satUnion('poloc', 'com', events))
    
    ### Communication relations for PSO
    enc = And(enc, satUnion('(ws+fr)', 'rfe', events, 'com-pso'))
    
    ### Program order for PSO
    enc = And(enc, satIntersection('po', 'RM', events))
    enc = And(enc, satUnion('(po&RM)', 'sync', events, 'po-pso'))
    
    ### Global happens before for PSO
    enc = And(enc, satUnion('po-pso', 'com-pso', events, 'ghb-pso'))
    
    return enc

def PsoConsistent(m):
    events = [e for e in m.events() if isinstance(e, (Load, Store, Init))]
    
    return And(satAcyclic('(poloc+com)', events), satAcyclic('ghb-pso', events))

def PsoInconsistent(m):
    events = [e for e in m.events() if isinstance(e, (Load, Store, Init))]
    
    return Or(satCycle('(poloc+com)', events), satCycle('ghb-pso', events))