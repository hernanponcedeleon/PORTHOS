from z3 import And, Or, Not
from types import NoneType

numOperations = ["+", "-", "*", "/", "%", "xor"]
numComparisons = ["==", "!=", "<", "<=", ">", ">=",]
boolOperations = ["and", "or", "not"]

### Predicate := Bool | Expression | Predicate And Predicate | Predicate Or Predicate | Not Predicate
class Predicate:
    
    def __init__(self, p1, op=None, p2=None):
        assert(isinstance(p1, (bool, Predicate)))
        assert(isinstance(p2, (bool, Predicate, NoneType)))
        #assert(op in numComparisons if isinstance(p1, Expression) and isinstance(p2, Expression) else op in boolOperations or op == None)
        assert(p2 == None if op == "not" else True)
        assert(isinstance(p1, bool) and p2 == None if op == None else True)
        self.op = op
        self.p1 = p1
        self.p2 = p2
    
    def __str__(self):
        if self.p2 != None: return "(%s %s %s)" % (str(self.p1), self.op, str(self.p2))
        elif self.op == "not": return "%s (%s)" % (self.op, str(self.p1))
        else: return str(self.p1)
    
    def encode(self, mapping):
        """ Returns a constraint representing the predicate and renaming the variables to satisfy SA. """
        ### The mapping is used for the renaming
        p1 = self.p1.encode(mapping) if not isinstance(self.p1, bool) else self.p1
        p2 = self.p2.encode(mapping) if not isinstance(self.p2, (bool, NoneType)) else self.p2
        if self.op == None: return self.p1
        if self.op == "==": return p1 == p2
        elif self.op == "!=": return p1 != p2
        elif self.op == ">": return p1 > p2
        elif self.op == ">=": return p1 >= p2
        elif self.op == "<": return p1 < p2
        elif self.op == "<=": return p1 <= p2
        elif self.op == "and": return And(p1, p2)
        elif self.op == "or": return Or(p1, p2)
            #elif self.op == "not": return Not(p1, p2)
        elif self.op == "not": return Not(p1)
        else: raise Exception("Type error in Predicate encode")