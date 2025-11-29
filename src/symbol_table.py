# symbol_table.py
from typing import Optional, List

# ---------------------------
# Object & Type enums
# ---------------------------
class ObjKind:
    VARIABLE = "variable"
    CONSTANT = "constant"
    TYPE = "type"
    FUNCTION = "function"
    PROCEDURE = "procedure"
    PARAMETER = "parameter"
    PROGRAM = "program"
    RESERVED = "reserved"

class TypeKind:
    UNKNOWN = 0
    INTEGER = 1
    REAL = 2
    BOOLEAN = 3
    CHAR = 4
    STRING = 5
    ARRAY = 6
    RECORD = 7

    @staticmethod
    def to_string(type_code):
        names = {
            TypeKind.UNKNOWN: "unknown",
            TypeKind.INTEGER: "integer",
            TypeKind.REAL: "real",
            TypeKind.BOOLEAN: "boolean",
            TypeKind.CHAR: "char",
            TypeKind.STRING: "string",
            TypeKind.ARRAY: "array",
            TypeKind.RECORD: "record",
        }
        # if a caller passes a string (older code), return it directly
        if isinstance(type_code, str):
            return type_code
        return names.get(type_code, f"type_{type_code}")

# ---------------------------
# Table entry dataclasses
# ---------------------------
class SymbolTableEntry:
    def __init__(self, identifier: str, link: int, obj: str, typ: int, ref: int, nrm: int, lev: int, adr: int):
        self.identifier = identifier  # name
        self.link = link              # index of previous symbol in same block (-1 if none)
        self.obj = obj                # ObjKind
        self.type = typ               # TypeKind (int) or custom (string)
        self.ref = ref                # reference (e.g. atab index)
        self.nrm = nrm                # normal / parameter flags
        self.lev = lev                # lexical level
        self.adr = adr                # address / offset

    def __repr__(self):
        return (f"<TAB id='{self.identifier}' obj={self.obj} type={TypeKind.to_string(self.type)} "
                f"ref={self.ref} nrm={self.nrm} lev={self.lev} adr={self.adr} link={self.link}>")

class BlockTableEntry:
    def __init__(self, lpar: int = 0):
        self.last: int = 0  # index into tab of last symbol in this block (-1 if none)
        self.lpar: int = lpar  # parent block index
        self.psze: int = 0   # parameter size
        self.vsze: int = 0   # variable size (count)

    def __repr__(self):
        return f"<BTAB last={self.last} lpar={self.lpar} psze={self.psze} vsze={self.vsze}>"

class ArrayTableEntry:
    def __init__(self, xtyp: int, etyp: int, eref: int, low: int, high: int, elsz: int, size: int):
        self.xtyp = xtyp
        self.etyp = etyp
        self.eref = eref
        self.low = low
        self.high = high
        self.elsz = elsz
        self.size = size

    def __repr__(self):
        return (f"<ATAB xtyp={TypeKind.to_string(self.xtyp)} etyp={TypeKind.to_string(self.etyp)} "
                f"eref={self.eref} low={self.low} high={self.high} elsz={self.elsz} size={self.size}>")

# ---------------------------
# SymbolTables (final, correct)
# ---------------------------
class SymbolTables:
    def __init__(self):
        # main tables
        self.tab: List[SymbolTableEntry] = []
        self.btab: List[BlockTableEntry] = []
        self.atab: List[ArrayTableEntry] = []

        # display[level] -> index into btab of active block at that lexical level
        self.display: List[int] = [0]
        self.level: int = 0

        # initialize reserved words (these occupy tab index 0..28)
        self._init_reserved_words()

        # create global block (level 0)
        self.enter_block()   # now level == 0

        # initialize predefined procedures (placed in global block)
        self._init_predefined()

    # ---------------------------
    # initialization helpers
    # ---------------------------
    def _init_reserved_words(self):
        reserved = [
            "AND", "ARRAY", "BEGIN", "CASE", "CONST", "DIV", "DOWNTO", "DO",
            "ELSE", "END", "FOR", "FUNCTION", "IF", "MOD", "NOT", "OF", "OR",
            "PROCEDURE", "PROGRAM", "RECORD", "REPEAT", "STRING", "THEN", "TO",
            "TYPE", "UNTIL", "VAR", "WHILE", "PACKED"
        ]
        # reserved have level -1 (not part of normal lexical levels)
        for w in reserved:
            entry = SymbolTableEntry(
                identifier=w,
                link=0,
                obj=ObjKind.RESERVED,
                typ=TypeKind.UNKNOWN,
                ref=0,
                nrm=0,
                lev=0,
                adr=0
            )
            self.tab.append(entry)

    def _init_predefined(self):
        predefined = ["writeln", "write", "readln", "read"]
        for name in predefined:
            # add into current block (global)
            self.add_symbol(identifier=name, obj=ObjKind.PROCEDURE, typ=TypeKind.UNKNOWN, nrm=0)

    # ---------------------------
    # block management
    # ---------------------------
    def enter_block(self) -> int:
        """Enter a new lexical block. Returns new level."""
        self.level += 1
        parent_bindex = self.display[self.level - 1] if self.level > 0 and self.level - 1 < len(self.display) else -1
        new_bindex = len(self.btab)
        self.btab.append(BlockTableEntry(lpar=parent_bindex))
        # ensure display list has slot for this level
        if self.level >= len(self.display):
            self.display.append(new_bindex)
        else:
            self.display[self.level] = new_bindex
        return self.level

    def exit_block(self) -> int:
        """Exit current block: returns new current level."""
        if self.level <= 0:
            # keep global as minimum
            self.level = 0
            return self.level
        self.level -= 1
        return self.level

    # ---------------------------
    # add / find symbols
    # ---------------------------
    def add_symbol(self, identifier: str, obj: str, typ: int = TypeKind.UNKNOWN,
                   ref: int = 0, nrm: int = 1, adr: int = 0) -> int:
        """Add symbol into current block. Returns 0-based tab index."""
        if self.level < 0:
            raise RuntimeError("No block active when adding symbol")

        current_bindex = self.display[self.level]
        if not (0 <= current_bindex < len(self.btab)):
            # defensive: if display points outside, create block
            current_bindex = len(self.btab)
            self.btab.append(BlockTableEntry(lpar=-1))
            self.display[self.level] = current_bindex

        prev_last = self.btab[current_bindex].last  # previous last tab index (0-based) or -1

        new_idx = len(self.tab)  # 0-based index for new entry

        entry = SymbolTableEntry(
            identifier=identifier,
            link=prev_last,
            obj=obj,
            typ=typ,
            ref=ref,
            nrm=nrm,
            lev=self.level,
            adr=adr
        )

        self.tab.append(entry)

        # update block last pointer to new index
        self.btab[current_bindex].last = new_idx

        # update variable area size if variable
        if obj == ObjKind.VARIABLE:
            self.btab[current_bindex].vsze += 1

        return new_idx

    def find_in_current_block(self, name: str) -> Optional[int]:
        """Return tab index if 'name' declared in current block (else None)."""
        if self.level < 0 or self.level >= len(self.display):
            return None
        bidx = self.display[self.level]
        if not (0 <= bidx < len(self.btab)):
            return None
        idx = self.btab[bidx].last
        visited = set()
        while idx != 0 and idx not in visited:
            visited.add(idx)
            entry = self.tab[idx]
            if entry.identifier.lower() == name.lower() and entry.lev == self.level:
                return idx
            idx = entry.link
        return None

    def lookup(self, name: str) -> Optional[int]:
        """Lexical lookup: from current level down to global (0), return tab index or None.
           Also check reserved words (level -1) which occupy tab[0..28].
        """
        # check reserved words first (they occupy the very first entries)
        for i in range(min(29, len(self.tab))):
            if self.tab[i].identifier.lower() == name.lower():
                return i

        for lvl in range(self.level, -1, -1):
            if lvl >= len(self.display):
                continue
            bidx = self.display[lvl]
            if not (0 <= bidx < len(self.btab)):
                continue
            idx = self.btab[bidx].last
            visited = set()
            while idx != 0 and idx not in visited:
                visited.add(idx)
                entry = self.tab[idx]
                if entry.identifier.lower() == name.lower():
                    return idx
                idx = entry.link
        return None

    # ---------------------------
    # arrays
    # ---------------------------
    def add_array_type(self, xtyp: int, etyp: int, eref: int, low: int, high: int, elsz: int) -> int:
        size = (high - low + 1) * elsz
        idx = len(self.atab)
        self.atab.append(ArrayTableEntry(xtyp=xtyp, etyp=etyp, eref=eref, low=low, high=high, elsz=elsz, size=size))
        return idx

    # ---------------------------
    # getters
    # ---------------------------
    def get_tab_entry(self, tab_index: int) -> Optional[SymbolTableEntry]:
        return self.tab[tab_index] if 0 <= tab_index < len(self.tab) else None

    def get_btab_entry(self, btab_index: int) -> Optional[BlockTableEntry]:
        return self.btab[btab_index] if 0 <= btab_index < len(self.btab) else None

    def get_atab_entry(self, atab_index: int) -> Optional[ArrayTableEntry]:
        return self.atab[atab_index] if 0 <= atab_index < len(self.atab) else None
