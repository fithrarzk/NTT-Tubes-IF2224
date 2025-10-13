"Buat definisi struktur data token nya yang bakal lewat lexical analysis"

from dataclasses import dataclass

@dataclass
class Token:
    type: str
    value: str | None = None
    line: int = 0
    column: int = 0

    def __str__(self):
        if self.value is None:
            return f"{self.type}"
        return f"{self.type}({self.value})"