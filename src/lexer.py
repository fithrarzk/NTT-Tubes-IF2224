from typing import List
from .dfa_load import DFARules
from .token import Token

class LexerError(Exception):
    pass

class Lexer:
    def __init__(self, dfa: DFARules):
        self.dfa = dfa
        self.keywords = dfa.keywords

    def tokenize(self, text: str) -> List[Token]:
        tokens: List[Token] = []
        i = 0
        line = 1
        col = 1
        n = len(text)

        while i < n:
            ch = text[i]

            # whitespace
            if ch.isspace():
                if ch == '\n':
                    line += 1
                    col = 1
                else:
                    col += 1
                i += 1
                continue

            # comments: { ... }
            if ch == '{':
                i += 1
                col += 1
                while i < n and text[i] != '}':
                    if text[i] == '\n':
                        line += 1
                        col = 1
                    else:
                        col += 1
                    i += 1
                if i < n and text[i] == '}':
                    i += 1
                    col += 1
                    continue
                else:
                    raise LexerError(f"Unterminated comment starting at line {line} col {col}")

            # comments: (* ... *)
            if ch == '(' and i+1 < n and text[i+1] == '*':
                i += 2
                col += 2
                while i+1 < n and not (text[i] == '*' and text[i+1] == ')'):
                    if text[i] == '\n':
                        line += 1
                        col = 1
                    else:
                        col += 1
                    i += 1
                if i+1 < n and text[i] == '*' and text[i+1] == ')':
                    i += 2
                    col += 2
                    continue
                else:
                    raise LexerError(f"Unterminated comment starting at line {line} col {col}")

            # string literal
            if ch == "'":
                start_col = col
                i += 1
                col += 1
                value_chars = []
                while i < n:
                    if text[i] == "'":
                        if i+1 < n and text[i+1] == "'":
                            value_chars.append("'")
                            i += 2
                            col += 2
                            continue
                        else:
                            i += 1
                            col += 1
                            break
                    else:
                        if text[i] == '\n':
                            line += 1
                            col = 1
                        else:
                            col += 1
                        value_chars.append(text[i])
                        i += 1
                else:
                    raise LexerError(f"Unterminated string starting at line {line} col {start_col}")
                tokens.append(Token('STRING_LITERAL', ''.join(value_chars), line, start_col))
                continue

            # cek float sama range operation (..) sekaligus scientific notation
            if ch.isdigit():
                start_col = col
                start_i = i
                has_dot = False
                has_notation = False

                # ambil semua digit awal
                while i < n and text[i].isdigit():
                    i += 1
                    col += 1

                # cek jika setelah digit ada titik
                if i < n and text[i] == '.':
                    # kalau dua titik, berarti RANGE
                    if i+1 < n and text[i+1] == '.':
                        num = text[start_i:i]
                        tokens.append(Token('NUMBER', num, line, start_col))
                        tokens.append(Token('RANGE_OPERATOR', '..', line, col))
                        i += 2
                        col += 2
                        continue
                    # kalau titik diikuti digit, berarti FLOAT
                    elif i+1 < n and text[i+1].isdigit():
                        has_dot = True
                        i += 1
                        col += 1
                        while i < n and text[i].isdigit():
                            i += 1
                            col += 1
                        num = text[start_i:i]
                        tokens.append(Token('NUMBER', num, line, start_col))
                        continue
                    else:
                        # titik tunggal setelah angka = error ngikut Pascal
                        raise LexerError(f"Invalid float format at line {line} col {col}: number cannot end with '.'")
                                # cek jika setelah digit ada titik

                if i < n and text[i] == 'E' or text[i] == 'e':
                    # kalau angka masuk
                    if i+1 < n and text[i+1].isdigit():
                        has_notation = True
                        i += 1
                        col += 1
                        while i < n and text[i].isdigit():
                            i += 1
                            col += 1
                        num = text[start_i:i]
                        tokens.append(Token('NUMBER', num, line, start_col))
                        continue
                    # kalau mines terus angka masuk juga
                    elif i+1 < n and text[i+1] == "-" and text[i+2].isdigit():
                        has_notation = True
                        i += 1
                        col += 1
                        while i < n and text[i].isdigit() or text[i] == '-':
                            i += 1
                            col += 1
                        num = text[start_i:i]
                        tokens.append(Token('NUMBER', num, line, start_col))
                        continue
                    else:
                        # titik tunggal setelah angka = error ngikut Pascal
                        raise LexerError(f"Invalid scientific notaion format at line {line} col {col}")

                # kalau tidak ada titik atau notasi setelah angka
                num = text[start_i:i]
                tokens.append(Token('NUMBER', num, line, start_col))
                continue

            # titik tunggal di luar angka
            if ch == '.':
                if i+1 < n and text[i+1] == '.':
                    tokens.append(Token('RANGE_OPERATOR', '..', line, col))
                    i += 2
                    col += 2
                    continue
                else:
                    tokens.append(Token('DOT', '.', line, col))
                    i += 1
                    col += 1
                    continue

            # transisi token lain
            start_i = i
            start_col = col
            state = self.dfa.start_state
            last_accept_pos = None
            last_accept_state = None

            j = i
            while j < n:
                chj = text[j]
                ns, consume = self.dfa.next_state(state, chj)
                if ns is None:
                    break
                if consume:
                    j += 1
                state = ns
                if self.dfa.is_final(state):
                    last_accept_pos = j
                    last_accept_state = state
                if not consume:
                    break

            if last_accept_pos is not None:
                token_info = self.dfa.get_token_for_final(last_accept_state)
                raw = text[start_i:last_accept_pos]
                tok_type = token_info.get('token')
                tok_value = token_info.get('value')

                # cek keyword
                if tok_type == 'IDENTIFIER':
                    if raw.lower() in self.keywords:
                        tokens.append(Token('KEYWORD', raw, line, start_col))
                    else:
                        tokens.append(Token('IDENTIFIER', raw, line, start_col))
                else:
                    value = tok_value if tok_value is not None else raw
                    tokens.append(Token(tok_type, value, line, start_col))

                for c in text[start_i:last_accept_pos]:
                    if c == '\n':
                        line += 1
                        col = 1
                    else:
                        col += 1
                i = last_accept_pos
                continue

            raise LexerError(f"Unrecognized token starting at line {line} col {col}: '{ch}'")

        return tokens
