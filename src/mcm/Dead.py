from Encoding import *

def Dead(m):
    events = [e for e in m.events() if isinstance(e, (Load, Store, Init))]
    
    ### New to handle RF not reading from init
    enc = satMinus('rf', 'IM', events, 'rf2')
    enc = And(enc, satMinus('ws', 'IM', events, 'ws2'))
    
    ### Dead (35)
    enc = And(enc, satDomRanIncl('ctrl', 'rf2', events))
    
    ### Dead (36.1)
    enc = And(enc, satImm('ws2', events))
    enc = And(enc, satComp('imm(ws2)', 'imm(ws2)', events))
    enc = And(enc, satInverse('ws2', events))
    enc = And(enc, satImm('(ws2)^-1', events))
    enc = And(enc, satComp('(imm(ws2);imm(ws2))', 'imm((ws2)^-1)', events))
    
    ### Dead (36.2)
    enc = And(enc, satRefClos('rf2', events))
    enc = And(enc, satInverse('rf2', events))
    enc = And(enc, satRefClos('(rf2)^-1', events))
    enc = And(enc, satComp('po', '((rf2)^-1)?', events))
    enc = And(enc, satRefClos('(po;((rf2)^-1)?)', events))
    enc = And(enc, satComp('(rf2)?', '((po;((rf2)^-1)?))?', events))
    
    ### Dead (36.3)
    enc = And(enc, satIncl('((imm(ws2);imm(ws2));imm((ws2)^-1))', '((rf2)?;((po;((rf2)^-1)?))?)', events))
    
    return enc

def satInverse(rel, events):
    enc = True
    for e1, e2 in product(events, events):
        enc = And(enc, Implies(edge(rel,e1,e2), edge('(%s)^-1' %rel,e2,e1)))
        enc = And(enc, Implies(edge('(%s)^-1' %rel,e2,e1), edge(rel,e1,e2)))
    return enc

#def satFRInit(events):
#    enc = True
#    for e1, e2 in product(events, events):
#        if not isinstance(e2, Init) or not isinstance(e1, Load) or e1.loc != e2.loc:
#            enc = And(enc, Not(edge('frinit',e1,e2)))
#        else:
#            enc = And(enc, Implies(edge('fr',e1,e2), edge('frinit',e1,e2)))
#    return enc

def satDomRanIncl(r1, r2, events):
    enc = True
    for e1 in events:
        orClause1 = Or([edge(r1,e1,e2) for e2 in events])
        orClause2 = Or([edge(r2,e2,e1) for e2 in events])
        enc = And(enc, Implies(orClause1, orClause2))
    return enc

def satRefClos(r, events):
    enc = True
    for e in events:
        enc = And(enc, edge('(%s)?' %r,e,e))
    for e1, e2 in product(events, events):
        enc = And(enc, Implies(edge(r,e1,e2), edge('(%s)?' %r,e1,e2)))
        enc = And(enc, Implies(edge('(%s)?' %r,e1,e2), Or(edge(r,e1,e2), edge('id',e1,e2))))
    return enc

def satIncl(r1, r2, events):
    enc = True
    for e1, e2 in product (events, events):
        enc = And(enc, Implies(edge(r1,e1,e2), edge(r2,e1,e2)))
    return enc

def satImm(r, events):
    enc = satComp(r, r, events)
    enc = And(enc, satMinus(r, '(%s;%s)' %(r,r), events, 'imm(%s)' %r))
    return enc