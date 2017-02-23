from pyparsing import *
import Program as pp
import Store as st

digits = '0123456789'
alphaNum = alphas + digits
names = Word(alphaNum)
lpar  = Literal( '(' ).suppress()
rpar  = Literal( ')' ).suppress()
lcbra = Literal( '{' ).suppress()
rcbra = Literal( '}' ).suppress()

CompOp = Literal('==') | Literal('!=') | Literal('<=') | Literal('<') | Literal('>=') | Literal('>')
ArithOp = Literal('+') | Literal('-') | Literal('*') | Literal('/') | Literal('%')
BoolOp = Literal('and') | Literal('or')

ArithExpr = Forward()
ArithAtom = Word(digits) | names | Group(lpar + ArithExpr + rpar)
ArithExpr << ArithAtom + ZeroOrMore(ArithOp + ArithExpr)
ArithComp = Group(lpar + ArithExpr + CompOp + ArithExpr + rpar)

Local = Group(names + Literal('<-') + ArithExpr)
Load = Group(names + Literal('<-') + names)
Store = Group(names + Literal('=') + names)
Lfence = Literal('lfence')
Hfence = Literal('hfence')
Cfence = Literal('cfence')
Fence = Lfence | Hfence | Cfence
Com = Local | Load | Store | Fence

BoolExpr = Forward()
BoolAtom = Literal('True') | Literal('False') | Literal('true') | Literal('false') | ArithComp | Group(lpar + BoolExpr + rpar)
BoolExpr << BoolAtom + ZeroOrMore(BoolOp + BoolExpr)

Instruction = Forward()
If = Group(Literal('if') + BoolExpr + Optional(Literal('then').suppress()) + lcbra + Instruction + rcbra + Optional(Literal('else').suppress() + lcbra + Instruction + rcbra))
While = Group(Literal('while') + BoolExpr + lcbra + Instruction + rcbra)
Seq = Group((Com | While | If) + ZeroOrMore(Literal(';') + Instruction))
Instruction << (Seq | If | While)

Global = lcbra + ZeroOrMore(names + Literal(',').suppress()) + names + rcbra + LineEnd().suppress()
Thread = Literal('thread').suppress() + names.suppress() + lcbra + Instruction + rcbra + OneOrMore(LineEnd().suppress())
Program = Global + OneOrMore(Thread)

def parsedToExpr(x, locs, regs):
    if str(x).isdigit():
        return (pp.Expression(int(x)), regs)
    elif isinstance(x, str):
        if x in locs.keys(): raise Exception('Predicates can only refer to registers, \"%s\" is declared as a global variable' %x)
        if not x in regs.keys(): raise Exception('Local variable \"%s\" must be initialized before using it in a predicate' %x)
        return (regs[x], regs)
    elif len(x) == 3:
        (exp1, regs) = parsedToExpr(x[0], locs, regs)
        (exp2, regs) = parsedToExpr(x[2], locs, regs)
        return (pp.Expression(exp1, x[1], exp2), regs)
    else:
        raise Exception('Parsing problem with %s' %x)

def parsedToBool(x, locs, regs):
    if isinstance(x, ParseResults) and len(x) == 3 and x[1] in ["and", "or"]:
        (exp1, regs) = parsedToBool(x[0], locs, regs)
        (exp2, regs) = parsedToBool(x[2], locs, regs)
        return (pp.Predicate(exp1, x[1], exp2), regs)
    elif isinstance(x, ParseResults) and len(x) == 3 and x[1] in ["<", "<=", ">", ">=", "==", "!="]:
        (exp1, regs) = parsedToExpr(x[0], locs, regs)
        (exp2, regs) = parsedToExpr(x[2], locs, regs)
        return (pp.Predicate(exp1, x[1], exp2), regs)     
    elif isinstance(x, ParseResults) and len(x) == 2 and x[0] == "not":
        (exp, regs) = parsedToBool(x[1], locs, regs)
        return (pp.Predicate("not", exp, regs))
    elif str(x) in ["true", "True", "false", "False"]:
        b = str(x) == "true" or str(x) == "True"
        return (pp.Expression(b), regs)
    else: raise Exception('Problem while converting %s to Bool' %x)

def parsedToThread(x, locs, regs):
    if isinstance (x, ParseResults) and x[0] == "while":
        (expr, regs) = parsedToBool(x[1], locs, regs)
        (inst, regs) = parsedToThread(x[2], locs, regs)
        return (pp.While(expr, inst), regs)
    elif isinstance(x, ParseResults) and x[0] == "if":
        (exp, regs) = parsedToBool(x[1], locs, regs)
        (inst1, regs) = parsedToThread(x[2], locs, regs)
        if len(x) > 3: (inst2, regs) = parsedToThread(x[3], locs, regs)
        else: inst2 = pp.Skip()
        return (pp.If(exp, inst1, inst2), regs)
    elif isinstance(x, ParseResults) and len(x) > 2 and x[1] == ";":
        (inst1, regs) = parsedToThread(x[0], locs, regs)
        (inst2, regs) = parsedToThread(x[2], locs, regs)
        return (pp.Seq(inst1, inst2), regs)
    elif isinstance(x, ParseResults) and len(x) > 2 and x[1] == "=":
        if x[0] in regs.keys(): raise Exception('Left-hand side of \"%s\" must be a global variable, \"%s\" is used as a register' %(''.join(x), x[0]))
        if not x[0] in locs.keys(): raise Exception('Global variable \"%s\" must be declared' %x[0])
        if x[2] in locs.keys(): raise Exception('Right-hand side of \"%s\" must be a register, \"%s\" is declared as global variable' %(''.join(x), x[2]))
        if not x[2] in regs.keys(): raise Exception('Local variable \"%s\" must be initialized before using it in an assignement' %x[2])
        loc = locs[x[0]]
        reg = regs[x[2]]
        return (st.Store(loc, reg), regs)
    elif isinstance(x, ParseResults) and len(x) > 2 and x[1] == "<-" and x[2] in locs.keys():
        if x[2] in regs.keys(): raise Exception('Error: \"%s\" is used as a global variable and a register' %(''.join(x), x[2]))
        if x[0] in locs.keys(): raise Exception('Left-hand side of \"%s\2 must be a register, \"%s\" is declared as global variable' %(''.join(x), x[0]))
        if not x[0] in regs.keys(): regs[x[0]] = pp.Register(x[0])
        loc = locs[x[2]]
        reg = regs[x[0]]
        return (pp.Load(reg, loc), regs)
    elif isinstance(x, ParseResults) and len(x) > 2 and x[1] == "<-":
        if x[0] in locs.keys(): raise Exception('Left-hand side of \"%s\" must be a register, \"%s\" is declared as global variable' %(''.join(x), x[0]))
        if not x[0] in regs.keys(): regs[x[0]] = pp.Register(x[0])
        reg = regs[x[0]]
        if str(x[2]).isdigit():
            expr = pp.Expression(int(x[2]))
        elif x[2] in regs.keys():
            expr = regs[x[2]]
        elif isinstance(x[2], ParseResults):
            expr = parsedToExpr(x[2], locs, regs)[0] 
        else:
            raise Exception('\"%s\" must be an expression' %x[2])
        return (pp.Local(reg, expr), regs)
    elif x == "hfence":
        return (pp.Sync(), regs)
    elif x == "lfence":
        return (pp.Lwsync(), regs)
    elif x == "cfence":
        return (pp.Isync(), regs)
    else:
        return parsedToThread(x[0], locs, regs)

def parsePorthosFile(filename):
    f = open(filename,'r')
    text = "".join(f.readlines())
    parsed = Program.parseString(text)

    prog = pp.Program()
    locs = {}
    for x in parsed:
        if not isinstance(x, ParseResults): locs[x] = pp.Location(x)
        else: prog.add(parsedToThread(x, locs, {})[0])
    return prog
