# buat jalanin lexer di terminal

import argparse
import sys
from .dfa_load import DFARules
from .lexer import Lexer, LexerError
from .parser import Parser, ParserError

def main():
    parser = argparse.ArgumentParser(description='Pascal-S Lexer (Milestone 1)')
    parser.add_argument('source', help='Path to Pascal-S source file (.pas)')
    parser.add_argument('--dfa', default='dfa_rules.json', help='Path to DFA JSON rules file')
    args = parser.parse_args()

    try:
        dfa = DFARules.from_file(args.dfa)
    except Exception as e:
        print(f'Gagal load DFA Rules dari {args.dfa}: {e}', file=sys.stderr)
        sys.exit(2)

    try:
        with open(args.source, 'r', encoding='utf-8') as f:
            src_text = f.read()
    except Exception as e:
        print(f'Gagal baca file sumber {args.source}: {e}', file=sys.stderr)
        sys.exit(2)

    lexer = Lexer(dfa)
    try:
        tokens = lexer.tokenize(src_text)
    except LexerError as le:
        print('Lexer error:', le, file=sys.stderr)
        sys.exit(3)

    parser = Parser(tokens)
    try:
        list_tokens = parser.parse()
    except ParserError as pe:
        print('Parser error:', pe, file=sys.stderr)
        sys.exit(4)

    print_parse_tree(list_tokens)

def print_parse_tree(list_tokens):
    if not list_tokens:
        return
    
    active_levels = set()
    
    for idx, (token_str, depth) in enumerate(list_tokens):
        is_last = True
        for future_idx in range(idx + 1, len(list_tokens)):
            future_depth = list_tokens[future_idx][1]
            if future_depth < depth:
                break
            if future_depth == depth:
                is_last = False
                break
        
        prefix = ""
        for level in range(depth):
            if level in active_levels:
                prefix += "│   "
            else:
                prefix += "    "
        
        if depth > 0:
            if is_last:
                prefix += "└── "
                if depth in active_levels:
                    active_levels.remove(depth)
            else:
                prefix += "├── "
                active_levels.add(depth)
        
        print(f"{prefix}{token_str}")

if __name__ == '__main__':
    main()
