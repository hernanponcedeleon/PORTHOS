from Thread import *

class Skip(Thread):

    def __init__(self):
        self.pid = None
        self.thread = None
        ### The conditional level is used for pretty printing
        self.condLevel = 0

    def __str__(self):
        return "%sskip" %("  "*self.condLevel)

    def incCondLevel(self):
        """ Increments its conditional level. """
        self.condLevel += 1
        return self

    def decCondLevel(self):
        """ Decrements its conditional level. """
        self.condLevel -= 1
        return self

    def setProgramsID(self, x):
        """ Sets its pid. """
        self.pid = x
        return x + 1

    def setEventsID(self, x):
        ### Since it dos not have sub-threads and it is not an event, it does nothing
        return x

    def unroll(self, bound):
        return self

    def setMapLastMod(self, mapping): return mapping

    def setCondReg(self, regs): return self