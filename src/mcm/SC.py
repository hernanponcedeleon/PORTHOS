from Encoding import *

def Sc(m):
    events = [e for e in m.events() if isinstance(e, (Load, Store, Init))]
    
    ### All communication relations
    enc = satUnion('ws', 'fr', events)
    enc = And(enc, satUnion('(ws+fr)', 'rf', events, 'com'))
    
    ### Global happens before for SC
    enc = And(enc, satUnion('po', 'com', events, 'ghb-sc'))
    
    return enc

def ScConsistent(m):
    events = [e for e in m.events() if isinstance(e, (Load, Store, Init))]
    
    return satAcyclic('ghb-sc', events)

def ScInconsistent(m):
    events = [e for e in m.events() if isinstance(e, (Load, Store, Init))]
    
    return satCycle('ghb-sc', events)