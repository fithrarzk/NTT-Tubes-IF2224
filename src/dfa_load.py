"Baca dfa_rules.json dan bikin fungsi transisi DFA (dari start state, final state, next state)"

import json
from typing import Dict, Any, Tuple, Optional

class DFARules:
    def __init__(self, data: Dict[str, Any]):
        self.start_state = data.get('start_state')
        self.final_states = data.get('final_states', {})
        self.transitions = data.get('transitions', {})
        self.keywords = set(k.lower() for k in data.get('keywords', []))

    @classmethod
    def from_file(cls, path: str):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls(data)

    def is_final(self, state: str) -> bool:
        return state in self.final_states

    def get_token_for_final(self, state: str):
        return self.final_states.get(state)

    def next_state(self, state: str, ch: str) -> Tuple[Optional[str], bool]:
        state_map = self.transitions.get(state, {})

        # Handle EOF character specially
        if ch == '\0':
            if 'OTHER' in state_map:
                return (state_map['OTHER'], False)
            return (None, False)

        # 1. Coba bandingin karakter exact dulu
        if ch in state_map:
            return (state_map[ch], True)

        # 2. Coba klasifikasi karakter
        if ch.isalpha() and 'LETTER' in state_map:
            return (state_map['LETTER'], True)
        elif ch.isdigit() and 'DIGIT' in state_map:
            return (state_map['DIGIT'], True)

        # 3. OTHER transition - Jangan konsumsi karakter
        if 'OTHER' in state_map:
            return (state_map['OTHER'], False)

        # 4. Gaada transisi valid
        return (None, False)