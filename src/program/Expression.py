from Predicate import *
from types import NoneType

### Expression := Int | Location | Register | Expression Op Expression.
class Expression(Predicate):

    def __init__(self, v1, op=None, v2=None):
        assert(isinstance(v1, (int, Expression)))
        assert(isinstance(v2, (int, Expression, NoneType)))
        assert(op in numOperations or op == None)
        assert(isinstance(v1, int) and v2 == None if op == None else True)
        self.op = op
        self.v1 = v1
        self.v2 = v2

    def __str__(self):
        if self.op == None: return str(self.v1)
        else: return "(%s %s %s)" % (str(self.v1), self.op, str(self.v2))

    def encode(self, mapping):
        """ Returns a constraint representing the expression and renaming the variables to satisfy SA. """
        ### The mapping is used for the renaming
        v1 = self.v1.encode(mapping) if not isinstance(self.v1, int) else self.v1
        v2 = self.v2.encode(mapping) if not isinstance(self.v2, (int, NoneType)) else self.v2
        if self.op == None: return v1
        else:
            if self.op == "+": return v1 + v2
            elif self.op == "-": return v1 - v2
            elif self.op == "*": return v1 * v2
            elif self.op == "/": return v1 / v2
            elif self.op == "%": return v1 % v2
            elif self.op == "xor": return 1 if (v1 == 0 and v2 == 1) or (v1 == 1 and v2 == 0) else 0
            else: raise Exception("Type error in Expression encode")