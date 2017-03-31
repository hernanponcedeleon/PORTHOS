from Encoding import *

def Dead(m):
    events = [e for e in m.events() if isinstance(e, (Load, Store, Init))]
    
    ### New to handle RF not reading from init
    enc = satMinus('rf', 'IM', events, 'rf2')
    enc = And(enc, satMinus('co', 'IM', events, 'co2'))
    
    ### Dead (35)
    enc = And(enc, satDomRanIncl('ctrl', 'rf2', events))
    
    ### Dead (36.1)
    enc = And(enc, satImm('co2', events))
    enc = And(enc, satComp('imm(co2)', 'imm(co2)', events))
    enc = And(enc, satInverse('co2', events))
    enc = And(enc, satImm('(co2)^-1', events))
    enc = And(enc, satComp('(imm(co2);imm(co2))', 'imm((co2)^-1)', events))
    
    ### Dead (36.2)
    enc = And(enc, satRefClos('rf2', events))
    enc = And(enc, satInverse('rf2', events))
    enc = And(enc, satRefClos('(rf2)^-1', events))
    enc = And(enc, satComp('po', '((rf2)^-1)?', events))
    enc = And(enc, satRefClos('(po;((rf2)^-1)?)', events))
    enc = And(enc, satComp('(rf2)?', '((po;((rf2)^-1)?))?', events))
    
    ### Dead (36.3)
    enc = And(enc, satIncl('((imm(co2);imm(co2));imm((co2)^-1))', '((rf2)?;((po;((rf2)^-1)?))?)', events))
    
    return enc
