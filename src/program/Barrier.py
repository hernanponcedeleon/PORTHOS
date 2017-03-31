from Event import *

class Barrier(Event):

    def __init__(self):
        self.pid = None
        self.eid = None
        self.z3id = id(self)
        self.thread = None
        self.condLevel = 0
        self.mapLastMod = {}

    def __str__(self):
        return "%sfence" %("  "*self.condLevel)

    def __repr__(self):
        return "P%s" % str(self.pid)

    def setMapLastMod(self, mapping):
        self.mapLastMod = mapping
        return self.mapLastMod

class Mfence(Barrier):

    def __init__(self):
        self.pid = None
        self.eid = None
        self.z3id = id(self)
        self.thread = None
        self.condLevel = 0

    def __str__(self):
        return "%smfence" %("  "*self.condLevel)

class Sync(Barrier):

    def __init__(self):
        self.pid = None
        self.eid = None
        self.z3id = id(self)
        self.thread = None
        self.condLevel = 0

    def __str__(self):
        return "%ssync" %("  "*self.condLevel)

class Lwsync(Barrier):

    def __init__(self):
        self.pid = None
        self.eid = None
        self.z3id = id(self)
        self.thread = None
        self.condLevel = 0

    def __str__(self):
        return "%slwsync" %("  "*self.condLevel)

class Isync(Barrier):

    def __init__(self):
        self.pid = None
        self.eid = None
        self.z3id = id(self)
        self.thread = None
        self.condLevel = 0

    def __str__(self):
        return "%sisync" %("  "*self.condLevel)