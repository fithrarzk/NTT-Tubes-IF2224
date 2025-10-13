"Lexical Analysis nya ya"
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

            # string literal (petik satu). Pascal pake ''.
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

            # DFA buat longest match (maximal munch)
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

                # Pindah ke next state
                state = ns
                
                # Cek current state if final
                if self.dfa.is_final(state):
                    if consume:
                        # Normal transition - terima setelah consume karakter
                        last_accept_pos = j + 1
                    else:
                        # OTHER transition - terima tanpa consume karakter
                        last_accept_pos = j
                    last_accept_state = state

                if consume:
                    j += 1
                else:
                    # OTHER transition - jangan proses tapi lanjut ke next iterasi
                    break

            # Process accepted token
            if last_accept_pos is not None:
                token_info = self.dfa.get_token_for_final(last_accept_state)
                raw = text[start_i:last_accept_pos]
                tok_type = token_info.get('token')
                tok_value = token_info.get('value')
                
                # Cek keyword
                if tok_type == 'IDENTIFIER':
                    if raw.lower() in self.keywords:
                        tokens.append(Token('KEYWORD', raw, line, start_col))
                    else:
                        tokens.append(Token('IDENTIFIER', raw, line, start_col))
                elif tok_type == 'NUMBER':
                    tokens.append(Token('NUMBER', raw, line, start_col))
                else:
                    value = tok_value if tok_value is not None else raw
                    tokens.append(Token(tok_type, value, line, start_col))
                
                # Update posisi
                consumed = text[start_i:last_accept_pos]
                for c in consumed:
                    if c == '\n':
                        line += 1
                        col = 1
                    else:
                        col += 1
                i = last_accept_pos
                continue

            # Kalau ga ada longest match, coba single character token
            # buat handle kaya '.' which go S0 -> DOT_OR_RANGE -> DOT (via OTHER)
            ns_first, consume_first = self.dfa.next_state(self.dfa.start_state, ch)
            if ns_first:
                if self.dfa.is_final(ns_first):
                    # Direct single character token
                    token_info = self.dfa.get_token_for_final(ns_first)
                    tok_type = token_info.get('token')
                    tok_value = token_info.get('value')
                    value = tok_value if tok_value is not None else ch
                    tokens.append(Token(tok_type, value, line, col))
                else:
                    # Coba OTHER transition dari state pertama
                    # handles cases like '.' -> DOT_OR_RANGE -> DOT
                    ns_other, consume_other = self.dfa.next_state(ns_first, ch if i+1 < n else '\0')
                    if not consume_other and self.dfa.is_final(ns_other):
                        token_info = self.dfa.get_token_for_final(ns_other)
                        tok_type = token_info.get('token')
                        tok_value = token_info.get('value')
                        value = tok_value if tok_value is not None else ch
                        tokens.append(Token(tok_type, value, line, col))
                    else:
                        raise LexerError(f"Unrecognized token starting at line {line} col {col}: '{ch}'")
                
                # Update posisi karakter single
                if ch == '\n':
                    line += 1
                    col = 1
                else:
                    col += 1
                i += 1
                continue

            raise LexerError(f"Unrecognized token starting at line {line} col {col}: '{ch}'")

        return tokens