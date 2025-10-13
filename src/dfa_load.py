"Baca dfa_rules.json dan bikin fungsi transisi DFA (dari start state, final state, next state)"

import json
from typing import Dict, Any

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

    def next_state(self, state: str, ch: str):
        state_map = self.transitions.get(state, {})
        # classification
        if ch.isalpha():
            key = 'LETTER'
        elif ch.isdigit():
            key = 'DIGIT'
        else:
            key = ch  # keep symbol (kaya ':', '.', dst.)

        # cek pemetaannya
        if key in state_map:
            return state_map[key]
        # kalau nemu
        if ch.isalpha() and 'LETTER' in state_map:
            return state_map['LETTER']
        if ch.isdigit() and 'DIGIT' in state_map:
            return state_map['DIGIT']
        # fallback ke yang lain
        if 'OTHER' in state_map:
            return state_map['OTHER']
        # gada transisi
        return None
