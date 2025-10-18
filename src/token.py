"Buat definisi struktur data token nya yang bakal lewat lexical analysis"

from dataclasses import dataclass

@dataclass
class Token:
    type: str
    value: str
    line: int
    column: int
    
    def __str__(self):
        if self.type == 'STRING_LITERAL':
            return f"{self.type}('{self.value}')" 
        else:
            return f"{self.type}({self.value})"