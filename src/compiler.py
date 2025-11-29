import argparse
import sys
from typing import Optional, Tuple
from .dfa_load import DFARules
from .lexer import Lexer, LexerError
from .parser import Parser, ParserError
from .symbol_table import SymbolTables, TypeKind, ObjKind
from .type_checker import TypeChecker
from .ast_nodes import ASTNode

class PascalCompiler:
    
    def __init__(self, dfa_path: str = 'dfa_rules.json', verbose: bool = False):
        self.dfa_path = dfa_path
        self.verbose = verbose
        
        self.dfa = None
        self.source_code = None
        self.tokens = None
        self.ast_root = None
        self.symbol_tables = None
        self.type_checker = None
        
        self.stats = {
            'tokens': 0,
            'symbols': 0,
            'blocks': 0,
            'arrays': 0
        }
        
    def compile(self, source_path: str) -> Tuple[bool, Optional[str]]:
        try:
            self._print_header("PASCAL-S COMPILER - MILESTONE 3")
            
            # Phase 1: Lexical Analysis
            success, error = self._phase1_lexical_analysis(source_path)
            if not success:
                return False, error
            
            # Phase 2: Syntax Analysis
            success, error = self._phase2_syntax_analysis()
            if not success:
                return False, error
            
            # Phase 3: Semantic Analysis
            success, error = self._phase3_semantic_analysis()
            if not success:
                return False, error
            
            # Display results
            self._display_results()
            
            self._print_header("COMPILATION SUCCESSFUL", "v")
            return True, None
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self._print_error(error_msg)
            if self.verbose:
                import traceback
                traceback.print_exc()
            return False, error_msg
    
    def _phase1_lexical_analysis(self, source_path: str) -> Tuple[bool, Optional[str]]:
        self._print_phase_header(1, "LEXICAL ANALYSIS")
        
        try:
            self.dfa = DFARules.from_file(self.dfa_path)
            self._print_success(f"DFA rules loaded from {self.dfa_path}")
            
            with open(source_path, 'r', encoding='utf-8') as f:
                self.source_code = f.read()
            self._print_success(f"Source file loaded: {source_path}")
            
            lexer = Lexer(self.dfa)
            self.tokens = lexer.tokenize(self.source_code)
            self.stats['tokens'] = len(self.tokens)
            self._print_success(f"Lexical analysis complete: {self.stats['tokens']} tokens generated")
            
            if self.verbose:
                self._print_tokens()
            
            return True, None
            
        except FileNotFoundError as e:
            return False, f"File not found: {source_path}"
        except LexerError as e:
            return False, f"Lexer error: {str(e)}"
        except Exception as e:
            return False, f"Phase 1 error: {str(e)}"
    
    def _phase2_syntax_analysis(self) -> Tuple[bool, Optional[str]]:
        self._print_phase_header(2, "SYNTAX ANALYSIS")
        
        try:
            parser = Parser(self.tokens)
            self.ast_root = parser.parse()
            self._print_success("Syntax analysis complete: AST constructed")
            
            return True, None
            
        except ParserError as e:
            return False, f"Parser error: {str(e)}"
        except Exception as e:
            return False, f"Phase 2 error: {str(e)}"
    
    def _phase3_semantic_analysis(self) -> Tuple[bool, Optional[str]]:
        self._print_phase_header(3, "SEMANTIC ANALYSIS")
        
        try:
            self.symbol_tables = SymbolTables()
            self._print_success("Symbol tables initialized")
            self._print_info(f"  - Reserved words: 29 entries (index 0-28)")
            self._print_info(f"  - Predefined procedures: {len(self.symbol_tables.tab) - 29} entries")
            
            self.type_checker = TypeChecker(self.symbol_tables)
            self._print_success("Starting semantic analysis...")
            
            self.type_checker.visit(self.ast_root)
            
            self.stats['symbols'] = len(self.symbol_tables.tab)
            self.stats['blocks'] = len(self.symbol_tables.btab)
            self.stats['arrays'] = len(self.symbol_tables.atab)
            
            self._print_success("Semantic analysis complete")
            self._print_info(f"  - Total symbols: {self.stats['symbols']}")
            self._print_info(f"  - Block levels: {self.stats['blocks']}")
            self._print_info(f"  - Array types: {self.stats['arrays']}")
            
            return True, None
            
        except TypeError as e:
            return False, f"Semantic error: {str(e)}"
        except Exception as e:
            return False, f"Phase 3 error: {str(e)}"
    
    def _display_results(self):
        print()
        
        self._display_symbol_table()
        self._display_block_table()
        self._display_array_table()
        
        self._display_decorated_ast()
    
    def _display_symbol_table(self):
        print("\n" + "=" * 90)
        print("SYMBOL TABLE (TAB)")
        print("=" * 90)
        print(f"{'Idx':<5} {'ID':<15} {'Obj':<12} {'Type':<12} {'Ref':<5} {'Nrm':<5} {'Lev':<5} {'Adr':<5} {'Link':<5}")
        print("-" * 90)
        
        for i, entry in enumerate(self.symbol_tables.tab):
            link_display = entry.link - 1 if entry.link > 0 else 0
            type_display = TypeKind.to_string(entry.type)
            
            print(f"{i:<5} {entry.identifier:<15} {entry.obj:<12} {type_display:<12} "
                  f"{entry.ref:<5} {entry.nrm:<5} {entry.lev:<5} {entry.adr:<5} {link_display:<5}")
    
    def _display_block_table(self):
        print("\n" + "=" * 90)
        print("BLOCK TABLE (BTAB)")
        print("=" * 90)
        print(f"{'Idx':<5} {'Last':<6} {'Lpar':<6} {'Psze':<6} {'Vsze':<6}")
        print("-" * 40)
        
        for i, block in enumerate(self.symbol_tables.btab):
            last_display = block.last - 1 if block.last > 0 else 0
            print(f"{i:<5} {last_display:<6} {block.lpar:<6} {block.psze:<6} {block.vsze:<6}")
    
    def _display_array_table(self):
        print("\n" + "=" * 90)
        print("ARRAY TABLE (ATAB)")
        print("=" * 90)
        
        if len(self.symbol_tables.atab) == 0:
            print("(empty - no arrays declared)")
        else:
            print(f"{'Idx':<5} {'Xtyp':<10} {'Etyp':<10} {'Eref':<6} {'Low':<6} {'High':<6} {'Elsz':<6} {'Size':<6}")
            print("-" * 65)
            
            for i, arr in enumerate(self.symbol_tables.atab):
                xtyp_display = TypeKind.to_string(arr.xtyp)
                etyp_display = TypeKind.to_string(arr.etyp)
                print(f"{i:<5} {xtyp_display:<10} {etyp_display:<10} {arr.eref:<6} "
                      f"{arr.low:<6} {arr.high:<6} {arr.elsz:<6} {arr.size:<6}")
    
    def _display_decorated_ast(self):
        print("\n" + "=" * 90)
        print("DECORATED ABSTRACT SYNTAX TREE")
        print("=" * 90)
        print()
        
        self._print_decorated_node(self.ast_root)
    
    def _print_decorated_node(self, node: ASTNode, indent: int = 0, prefix: str = "", is_last: bool = True):
        if node is None:
            return
        
        node_str = node.__class__.__name__
        if hasattr(node, 'name') and isinstance(node.name, str):
            node_str += f" '{node.name}'"
        elif hasattr(node, 'value') and not callable(node.value):
            if isinstance(node.value, str):
                node_str += f" '{node.value}'"
            else:
                node_str += f" {node.value}"
        elif hasattr(node, 'op') and isinstance(node.op, str):
            node_str += f" [{node.op}]"
        
        decorations = []
        
        if hasattr(node, 'type') and node.type is not None:
            if isinstance(node.type, int):
                decorations.append(f"type: {TypeKind.to_string(node.type)}")
        
        if hasattr(node, 'tab_index') and node.tab_index is not None:
            tab_entry = self.symbol_tables.get_tab_entry(node.tab_index)
            if tab_entry:
                decorations.append(f"tab[{node.tab_index}]")
                decorations.append(f"obj: {tab_entry.obj}")
                if tab_entry.lev > 0:
                    decorations.append(f"scope: {tab_entry.lev}")
        
        elif hasattr(node, 'scope_level') and node.scope_level is not None:
            decorations.append(f"scope: {node.scope_level}")
        
        if decorations:
            node_str += f" ({', '.join(decorations)})"
        
        if indent == 0:
            print(node_str)
        else:
            connector = "└── " if is_last else "├── "
            print(f"{prefix}{connector}{node_str}")
        
        children = self._get_child_nodes(node)
        
        if indent == 0:
            new_prefix = ""
        else:
            extension = "    " if is_last else "│   "
            new_prefix = prefix + extension
        
        for i, (label, child) in enumerate(children):
            is_last_child = (i == len(children) - 1)
            
            if label and self._has_multiple_same_label(children, label):
                label_connector = "└── " if is_last_child else "├── "
                print(f"{new_prefix}{label_connector}[{label}]")
                child_prefix = new_prefix + ("    " if is_last_child else "│   ")
                self._print_decorated_node(child, indent + 2, child_prefix, True)
            else:
                self._print_decorated_node(child, indent + 1, new_prefix, is_last_child)
    
    def _get_child_nodes(self, node: ASTNode):
        children = []
        
        if not hasattr(node, '__dict__'):
            return children
        
        attribute_order = [
            'declarations', 'params', 'return_type', 'block', 'compound_statement',
            'statements', 'condition', 'then_statement', 'else_statement',
            'body', 'target', 'value', 'left', 'right', 'operand',
            'array_var', 'index_expression', 'arguments',
            'start_expr', 'end_expr', 'var', 'low', 'high',
            'index_range', 'element_type', 'type_name'
        ]
        
        for attr_name in attribute_order:
            if hasattr(node, attr_name):
                attr_value = getattr(node, attr_name)
                
                if attr_value is None:
                    continue
                
                if attr_name in ('type', 'scope_level', 'tab_index', 'line', 'column',
                               'names', 'name', 'value', 'op', 'is_downto'):
                    continue
                
                if self._is_ast_node(attr_value):
                    children.append((attr_name, attr_value))
                
                elif isinstance(attr_value, list) and len(attr_value) > 0:
                    for item in attr_value:
                        if self._is_ast_node(item):
                            children.append((attr_name, item))
        
        return children
    
    def _is_ast_node(self, obj) -> bool:
        if not hasattr(obj, '__class__'):
            return False
        class_name = obj.__class__.__name__
        return 'Node' in class_name and hasattr(obj, '__dict__')
    
    def _has_multiple_same_label(self, children, label):
        count = sum(1 for l, _ in children if l == label)
        return count > 1
    
    def _print_tokens(self):
        print("\n  Tokens:")
        for i, token in enumerate(self.tokens):
            print(f"    {i:3d}. {token}")
    
    def _print_header(self, title: str, symbol: str = "="):
        print(f"\n{symbol * 90}")
        print(f"{title:^90}")
        print(f"{symbol * 90}")
    
    def _print_phase_header(self, phase: int, title: str):
        print(f"\n{'=' * 90}")
        print(f"PHASE {phase}: {title}")
        print(f"{'=' * 90}")
    
    def _print_success(self, message: str):
        print(f" {message}")
    
    def _print_info(self, message: str):
        print(f"  {message}")
    
    def _print_error(self, message: str):
        print(f"COMPILATION FAILED")
        print(f"{message}")
    
    def get_tokens(self):
        return self.tokens
    
    def get_ast(self):
        return self.ast_root
    
    def get_symbol_tables(self):
        return self.symbol_tables
    
    def get_statistics(self):
        return self.stats.copy()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Pascal-S Compiler - Milestone 3: Semantic Analysis'
    )
    parser.add_argument('source', help='Path to Pascal-S source file (.pas)')
    parser.add_argument('--dfa', default='dfa_rules.json', 
                       help='Path to DFA JSON rules file (default: dfa_rules.json)')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose output (shows tokens)')
    
    args = parser.parse_args()
    
    compiler = PascalCompiler(dfa_path=args.dfa, verbose=args.verbose)
    success, error = compiler.compile(args.source)
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
