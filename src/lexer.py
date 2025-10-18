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

            # DFA processing
            start_i = i
            start_col = col
            state = self.dfa.start_state
            last_accept_pos = None
            last_accept_state = None

            j = i
            while j <= n:
                if j < n:
                    chj = text[j]
                    ns, consume = self.dfa.next_state(state, chj)
                    print(f"DEBUG: From state '{state}' with char '{chj}' -> next_state='{ns}', consume={consume}")
                else:
                    # End of input - check if current state is final
                    if self.dfa.is_final(state):
                        last_accept_pos = j
                        last_accept_state = state
                        print(f"DEBUG: End of input, final state '{state}' accepted")
                    break
                
                if ns is None:
                    print(f"DEBUG: No transition found from state '{state}' with char '{chj}'")
                    break

                # Update state
                state = ns
                print(f"DEBUG: State updated to '{state}'")
                
                # Check if final and record position
                if self.dfa.is_final(state):
                    if consume:
                        last_accept_pos = j + 1  # Position after consuming character
                    else:
                        last_accept_pos = j      # Position at current character
                    last_accept_state = state
                    print(f"DEBUG: Final state '{state}' reached, accept_pos={last_accept_pos}")
                
                # Advance position if consuming
                if consume:
                    j += 1
                    print(f"DEBUG: Consumed char '{chj}', j advanced to {j}")
                else:
                    print(f"DEBUG: OTHER transition, breaking without consuming '{chj}'")

                    j+=1

            if last_accept_pos is not None:
                token_info = self.dfa.get_token_for_final(last_accept_state)
                raw = text[start_i:last_accept_pos]
                tok_type = token_info.get('token')
                tok_value = token_info.get('value')
                
                print(f"DEBUG: Accepted token: '{raw}' (state: {last_accept_state}, type: {tok_type})")

                # Handle string literals - extract content only
                if tok_type == 'STRING_LITERAL':
                    # Remove quotes and handle escapes
                    if len(raw) >= 2 and raw[0] == "'" and raw[-1] == "'":
                        string_content = raw[1:-1].replace("''", "'")
                        tokens.append(Token('STRING_LITERAL', string_content, line, start_col))
                    else:
                        tokens.append(Token('STRING_LITERAL', raw, line, start_col))
                elif tok_type == 'IDENTIFIER':
                        clean_raw = raw.rstrip('.')
                        if clean_raw.lower() in self.keywords:
                            tokens.append(Token('KEYWORD', clean_raw, line, start_col))
                            # Handle remaining dots
                            dots = raw[len(clean_raw):]
                            for dot in dots:
                                tokens.append(Token('DOT', '.', line, start_col + len(clean_raw)))
                        else:
                            tokens.append(Token('IDENTIFIER', raw, line, start_col))
                else:
                    value = tok_value if tok_value is not None else raw
                    tokens.append(Token(tok_type, value, line, start_col))

                # Update position
                for c in text[start_i:last_accept_pos]:
                    if c == '\n':
                        line += 1
                        col = 1
                    else:
                        col += 1
                i = last_accept_pos
                continue

            print(f"DEBUG: NO TOKEN ACCEPTED! Failed at char '{ch}' at position {i}")
            raise LexerError(f"Unrecognized token starting at line {line} col {col}: '{ch}'")

        return tokens