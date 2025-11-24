class SymbolTableEntry:
    def __init__(self, identifiers, link, obj, typ, ref, nrm, lev, adr):
        self.identifiers = identifiers
        self.link = link
        self.obj = obj
        self.type = typ
        self.ref = ref
        self.nrm = nrm
        self.lev = lev
        self.adr = adr

class BlockTableEntry:
    def __init__(self):
        self.last = 0
        self.lpar = 0
        self.psze = 0
        self.vsze = 0

class ArrayTableEntry:
    def __init__(self, xtyp, etyp, eref, low, high, elsz, size):
        self.xtyp = xtyp
        self.etyp = etyp
        self.eref = eref
        self.low = low
        self.high = high
        self.elsz = elsz
        self.size = size

class SymbolTables:
    def __init__(self):
        self.tab = []   # identifier table
        self.btab = [BlockTableEntry()]  # global block
        self.atab = []  # array table
        self.display = [0]  # stack of active blocks
        self.level = 0
