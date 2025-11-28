from typing import Optional, List
class ObjKind:
    VARIABLE = "variable"
    CONSTANT = "constant"
    TYPE = "type"
    FUNCTION = "function"
    PROCEDURE = "procedure"
    PARAMETER = "parameter"
    PROGRAM = "program"

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
    def __init__(self, identifier: str, link: int, obj: str, typ: str, ref: int, nrm: int, lev: int, adr: int):
        self.identifier = identifier
        self.link = link      
        self.obj = obj
        self.type = typ
        self.ref = ref
        self.nrm = nrm
        self.lev = lev
        self.adr = adr

    def __repr__(self):
        return (f"<TAB id='{self.identifier}' obj={self.obj} type={self.type} "
                f"ref={self.ref} nrm={self.nrm} lev={self.lev} adr={self.adr} link={self.link}>")

class BlockTableEntry:
    def __init__(self, lpar=0):
        self.last: int = 0     # 1-based index ke TAB, 0 kalau kosong
        self.lpar: int = lpar  # indeks parent block di BTAB (0-based), 0 untuk global block
        self.psze: int = 0     # parameter size
        self.vsze: int = 0     # variable size

    def __repr__(self):
        return f"<BTAB last={self.last} lpar={self.lpar} psze={self.psze} vsze={self.vsze}>"

class ArrayTableEntry:
    def __init__(self, xtyp: str, etyp: str, eref: int,
                 low: int, high: int, elsz: int, size: int):
        self.xtyp = xtyp
        self.etyp = etyp
        self.eref = eref
        self.low = low
        self.high = high
        self.elsz = elsz
        self.size = size

    def __repr__(self):
        return (f"<ATAB xtyp={self.xtyp} etyp={self.etyp} eref={self.eref} "
                f"low={self.low} high={self.high} elsz={self.elsz} size={self.size}>")

class SymbolTables:
    def __init__(self):
        # Inisialisasi sesuai spesifikasi Pascal-S
        self.tab: List[SymbolTableEntry] = []
        self.btab: List[BlockTableEntry] = [BlockTableEntry(lpar=0)]  # btab[0] = global block, lpar=0
        self.atab: List[ArrayTableEntry] = []
        self.display: List[int] = [0]  # display[level] = indeks btab
        self.level: int = 0  # lexical level (0 = global)

        # Initialize reserved words (indeks 0-28)
        self._init_reserved_words()
        
        # Initialize predefined procedures/functions (mulai dari indeks 29+)
        self._init_predefined()

    def _init_reserved_words(self):
        """Initialize reserved words di indeks 0-28"""
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
        predefined = [
            ("writeln", ObjKind.PROCEDURE),
            ("write", ObjKind.PROCEDURE),
            ("readln", ObjKind.PROCEDURE),
            ("read", ObjKind.PROCEDURE)
        ]
        
        for name, obj_kind in predefined:
            entry = SymbolTableEntry(
                identifier=name,
                link=0,
                obj=obj_kind,
                typ=TypeKind.UNKNOWN,
                ref=0,
                nrm=0,
                lev=0,
                adr=0
            )
            self.tab.append(entry)
    
    # helper
    def _tab_len_1based(self) -> int:
        return len(self.tab)

    def _new_tab_index_1based(self) -> int:
        return len(self.tab) + 1

    def lookup(self, name: str) -> Optional[int]:
        for lvl in range(self.level, -1, -1):
            block_idx = self.display[lvl]
            if block_idx < 0 or block_idx >= len(self.btab):
                continue
            i = self.btab[block_idx].last  # 1-based index
            while i != 0:
                entry = self.tab[i - 1]
                if entry.identifier == name:
                    return i - 1
                i = entry.link
        for idx, entry in enumerate(self.tab):
            if entry.identifier == name and entry.lev == 0 and entry.link == 0:
                if entry.obj in (ObjKind.PROCEDURE, ObjKind.FUNCTION, "reserved"):
                    return idx
        
        return None

    def find_in_current_block(self, name: str) -> Optional[int]:
        block_idx = self.display[self.level]
        i = self.btab[block_idx].last
        while i != 0:
            entry = self.tab[i - 1]
            if entry.identifier == name:
                return i - 1
            i = entry.link
        return None

    def add_symbol(self, identifier: str, obj: str, typ: str = TypeKind.UNKNOWN, ref: int = 0, nrm: int = 0, adr: int = 0) -> int:
        current_block = self.display[self.level]
        prev_last = self.btab[current_block].last  # 1-based index (atau 0 jika kosong)
        new_index_1based = self._new_tab_index_1based()

        entry = SymbolTableEntry(
            identifier=identifier,
            link=prev_last,  # Link menggunakan format 1-based (sama seperti btab.last)
            obj=obj,
            typ=typ,
            ref=ref,
            nrm=nrm,
            lev=self.level,
            adr=adr
        )
        self.tab.append(entry)

        # update btab.last for current block
        self.btab[current_block].last = new_index_1based

        return new_index_1based - 1  # return 0-based

    def enter_block(self) -> int:
        parent_block_idx = self.display[self.level]
        new_block_idx = len(self.btab)  # next BTAB index (0-based)
        new_bentry = BlockTableEntry()
        new_bentry.lpar = parent_block_idx
        # last/psze/vsze default 0
        self.btab.append(new_bentry)

        # update display and level
        self.level += 1
        self.display.append(new_block_idx)
        return self.level

    def exit_block(self) -> int:
        if self.level == 0:
            # global
            return 0
        self.display.pop()
        self.level -= 1
        return self.level

    def add_array_type(self, xtyp: str, etyp: str, eref: int, low: int, high: int, elsz: int) -> int:
        size = (high - low + 1) * elsz
        idx = len(self.atab)
        self.atab.append(ArrayTableEntry(xtyp=xtyp, etyp=etyp, eref=eref,
                                         low=low, high=high, elsz=elsz, size=size))
        return idx

    def get_tab_entry(self, tab_index_0based: int) -> Optional[SymbolTableEntry]:
        if 0 <= tab_index_0based < len(self.tab):
            return self.tab[tab_index_0based]
        return None

    def get_btab_entry(self, btab_index: int) -> Optional[BlockTableEntry]:
        if 0 <= btab_index < len(self.btab):
            return self.btab[btab_index]
        return None

    def get_atab_entry(self, atab_index: int) -> Optional[ArrayTableEntry]:
        if 0 <= atab_index < len(self.atab):
            return self.atab[atab_index]
        return None
