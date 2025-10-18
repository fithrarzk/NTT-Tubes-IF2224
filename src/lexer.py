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
        
        # tambahin EOF biar OTHER transitions bisa jalan
        text_with_eof = text + '\0'
        n = len(text_with_eof)

        while i < n - 1:  # berhenti sebelum EOF
            ch = text_with_eof[i]

            # skip whitespace
            if ch.isspace():
                if ch == '\n':
                    line += 1
                    col = 1
                else:
                    col += 1
                i += 1
                continue

            # mulai proses DFA
            start_i = i
            start_col = col
            state = self.dfa.start_state
            last_accept_pos = None
            last_accept_state = None

            j = i
            while j < n:
                chj = text_with_eof[j]
                ns, consume = self.dfa.next_state(state, chj)
                
                if ns is None:
                    break

                # update state
                state = ns
                
                # cek apakah final state
                if self.dfa.is_final(state):
                    if consume:
                        last_accept_pos = j + 1
                    else:
                        last_accept_pos = j
                    last_accept_state = state
                
                if consume:
                    j += 1
                else:
                    # OTHER transition tanpa konsumsi
                    j += 1

            if last_accept_pos is not None:
                # pastiin gak masukin EOF di token
                actual_end = min(last_accept_pos, len(text))
                token_info = self.dfa.get_token_for_final(last_accept_state)
                raw = text[start_i:actual_end]
                tok_type = token_info.get('token')
                tok_value = token_info.get('value')

                # handle string literal khusus
                if tok_type == 'STRING_LITERAL':
                    if len(raw) >= 2 and raw[0] == "'" and raw[-1] == "'":
                        string_content = raw[1:-1].replace("''", "'")
                        tokens.append(Token('STRING_LITERAL', string_content, line, start_col))
                    else:
                        tokens.append(Token('STRING_LITERAL', raw, line, start_col))
                elif tok_type == 'IDENTIFIER':
                    # cek keyword atau identifier biasa
                    if raw.lower() in self.keywords:
                        tokens.append(Token('KEYWORD', raw, line, start_col))
                    else:
                        tokens.append(Token('IDENTIFIER', raw, line, start_col))
                else:
                    value = tok_value if tok_value is not None else raw
                    tokens.append(Token(tok_type, value, line, start_col))

                # update posisi setelah ambil token
                for c in text[start_i:actual_end]:
                    if c == '\n':
                        line += 1
                        col = 1
                    else:
                        col += 1
                i = actual_end
                continue

            raise LexerError(f"Unrecognized token starting at line {line} col {col}: '{ch}'")

        return tokens