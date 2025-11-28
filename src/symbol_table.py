class ObjKind:
    VARIABLE = "variable"
    CONSTANT = "constant"
    TYPE = "type"
    FUNCTION = "function"
    PROCEDURE = "procedure"
    ARRAY = "array"


class TypeKind:
    UNKNOWN = 0
    INTEGER = 1
    REAL = 2
    BOOLEAN = 3
    CHAR = 4
    STRING = 5
    ARRAY = 6
    RECORD = 7
    
    # convert numeric code to string name
    @staticmethod
    def to_string(type_code):
        type_names = {
            0: "unknown",
            1: "integer",
            2: "real",
            3: "boolean",
            4: "char",
            5: "string",
            6: "array",
            7: "record"
        }
        if isinstance(type_code, int):
            return type_names.get(type_code, f"type_{type_code}")
        return str(type_code)  # For backward compatibility with string types

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
        
        # Initialize reserved words
        self._init_reserved_words()
        
        # Initialize predefined procedures/functions
        self._init_predefined()
    
    def _init_reserved_words(self):
        reserved = [
            "AND", "ARRAY", "BEGIN", "CASE", "CONST", "DIV", "DOWNTO", "DO",
            "ELSE", "END", "FOR", "FUNCTION", "IF", "MOD", "NOT", "OF", "OR",
            "PROCEDURE", "PROGRAM", "RECORD", "REPEAT", "STRING", "THEN", "TO",
            "TYPE", "UNTIL", "VAR", "WHILE", "PACKED"
        ]
        
        for word in reserved:
            entry = SymbolTableEntry(
                identifier=word,
                link=0,
                obj="reserved",
                typ=TypeKind.UNKNOWN,
                ref=0,
                nrm=0,
                lev=0,
                adr=0
            )
            self.tab.append(entry)
    
    def _init_predefined(self):
        # writeln
        writeln_entry = SymbolTableEntry(
            identifier="writeln",
            link=0,
            obj=ObjKind.PROCEDURE,
            typ=TypeKind.UNKNOWN,
            ref=0,
            nrm=0,
            lev=0,
            adr=0
        )
        self.tab.append(writeln_entry)
        
        # write
        write_entry = SymbolTableEntry(
            identifier="write",
            link=0,
            obj=ObjKind.PROCEDURE,
            typ=TypeKind.UNKNOWN,
            ref=0,
            nrm=0,
            lev=0,
            adr=0
        )
        self.tab.append(write_entry)
        
        # readln
        readln_entry = SymbolTableEntry(
            identifier="readln",
            link=0,
            obj=ObjKind.PROCEDURE,
            typ=TypeKind.UNKNOWN,
            ref=0,
            nrm=0,
            lev=0,
            adr=0
        )
        self.tab.append(readln_entry)
        
        # read
        read_entry = SymbolTableEntry(
            identifier="read",
            link=0,
            obj=ObjKind.PROCEDURE,
            typ=TypeKind.UNKNOWN,
            ref=0,
            nrm=0,
            lev=0,
            adr=0
        )
        self.tab.append(read_entry)

    def lookup(self, name):
        # Search level sekarang to global
        for lev in range(self.level, -1, -1):
            idx = self.display[lev]
            
            while idx != 0:
                entry = self.tab[idx]
                if entry.identifier.lower() == name.lower():
                    return idx
                idx = entry.link
        
        for i in range(min(len(self.tab), 33)):
            entry = self.tab[i]
            if entry.identifier.lower() == name.lower():
                return i
        
        return None

    def add_symbol(self, identifier, obj, typ=TypeKind.UNKNOWN, ref=0, nrm=0, adr=0):
        prev = self.display[self.level]
        
        new_index = len(self.tab)
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

        current_block_idx = self.display[self.level] if self.level < len(self.display) else 0
        if self.level < len(self.btab):
            self.btab[self.level].last = new_index

        return new_index 

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