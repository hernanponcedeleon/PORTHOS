from Encoding import *

def ScInconsistent(m):
    events = [e for e in m.events() if isinstance(e, (Load, Store, Init))]
    
    enc = satEq('po', 'ppoS', events)
    enc = And(enc, satUnion('ws', 'fr', events))
    enc = And(enc, satUnion('(ws+fr)', 'rf', events))
    enc = And(enc, satUnion('((ws+fr)+rf)', 'ppoS', events, 'ghbS'))
    enc = And(enc, satCycle('ghbS', events))
    
    return enc