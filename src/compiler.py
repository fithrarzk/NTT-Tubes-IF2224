# buat jalanin lexer di terminal

import argparse
import sys
from .dfa_load import DFARules
from .lexer import Lexer, LexerError

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

    for t in tokens:
        print(str(t))

if __name__ == '__main__':
    main()
