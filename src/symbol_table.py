class ObjKind:
    VARIABLE = "variable"
    CONSTANT = "constant"
    TYPE = "type"
    FUNCTION = "function"
    PROCEDURE = "procedure"
    ARRAY = "array"


class TypeKind:
    INTEGER = "integer"
    REAL = "real"
    BOOLEAN = "boolean"
    CHAR = "char"
    STRING = "string"
    ARRAY = "array"
    UNKNOWN = "unknown"

class SymbolTableEntry:
    def __init__(self, identifier, link, obj, typ, ref, nrm, lev, adr):
        self.identifier = identifier  
        self.link = link             
        self.obj = obj              
        self.type = typ             
        self.ref = ref                
        self.nrm = nrm                
        self.lev = lev              
        self.adr = adr                

    def __repr__(self):
        return (f"<TAB: id={self.identifier}, obj={self.obj}, type={self.type}, "f"ref={self.ref}, lev={self.lev}, adr={self.adr}, link={self.link}>")

class BlockTableEntry:
    def __init__(self):
        self.last = 0
        self.lpar = 0
        self.psze = 0
        self.vsze = 0

    def __repr__(self):
        return f"<BTAB last={self.last}, lpar={self.lpar}, psze={self.psze}, vsze={self.vsze}>"

class ArrayTableEntry:
    def __init__(self, xtyp, etyp, eref, low, high, elsz, size):
        self.xtyp = xtyp
        self.etyp = etyp
        self.eref = eref
        self.low = low
        self.high = high
        self.elsz = elsz
        self.size = size

    def __repr__(self):
        return (f"<ATAB xtyp={self.xtyp}, etyp={self.etyp}, eref={self.eref}, "f"low={self.low}, high={self.high}, size={self.size}>")

class SymbolTables:
    def __init__(self):
        self.tab = []
        self.btab = [BlockTableEntry()]  # block 0 = global block
        self.atab = []
        self.display = [0]               # pointer to tab index start for each level
        self.level = 0                   # lexical level

    def lookup(self, name):
        idx = self.display[self.level]  # pointer ke start
        while idx != 0:
            entry = self.tab[idx - 1] 
            if entry.identifier == name:
                return idx - 1
            idx = entry.link
        return None

    def add_symbol(self, identifier, obj, typ=TypeKind.UNKNOWN, ref=0, nrm=0, adr=0):
        prev = self.display[self.level]  
        new_index = len(self.tab) + 1   
        entry = SymbolTableEntry(
            identifier=identifier,
            link=prev,
            obj=obj,
            typ=typ,
            ref=ref,
            nrm=nrm,
            lev=self.level,
            adr=adr
        )
        self.tab.append(entry)
        self.display[self.level] = new_index 

        # update BTAB.last
        self.btab[self.level].last = new_index

        return new_index - 1 

    def enter_block(self):
        self.level += 1
        self.display.append(0)
        self.btab.append(BlockTableEntry())

        return self.level

    def exit_block(self):
        self.display.pop()
        self.level -= 1

    def add_array_type(self, xtyp, etyp, eref, low, high, elsz, size):
        idx = len(self.atab)
        self.atab.append(ArrayTableEntry(xtyp, etyp, eref, low, high, elsz, size))
        return idx  # atab index