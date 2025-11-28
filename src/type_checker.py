from .ast_nodes import *
from .symbol_table import *

class TypeChecker:
    def __init__(self, symbol_tables: SymbolTables):
        self.symbol_tables = symbol_tables
        self.current_function = None

    def error(self, message: str, node: ASTNode):
        raise TypeError(f"Type Error at line {node.line}, column {node.column}: {message}")
    
    def visit(self, node: ASTNode):
        if node is None:
            return None
        
        method_name = f'visit_{node.__class__.__name__}'
        visitor = getattr(self, method_name, self.generic_visit)

        result_type = visitor(node)
        if result_type is not None:
             node.type = result_type 

        return result_type
    
    def generic_visit(self, node: ASTNode):
        self.error(f"No visit method for {node.__class__.__name__}", node)
        return TypeKind.UNKNOWN
    
    def visit_ProgramNode(self, node: ProgramNode):
        prog_idx = len(self.symbol_tables.tab)
        prog_entry = SymbolTableEntry(
            identifier=node.name,
            link=0,
            obj="program",
            typ=TypeKind.UNKNOWN,
            ref=0,
            nrm=1,
            lev=0,
            adr=0
        )
        self.symbol_tables.tab.append(prog_entry)
        
        for decl in node.declarations:
            self.visit(decl)

        self.visit(node.block)

        node.scope_level = 0
        
        if len(self.symbol_tables.tab) > prog_idx:
            self.symbol_tables.btab[0].last = len(self.symbol_tables.tab) - 1

        return node
    
    def visit_BlockNode(self, node: BlockNode): 
        self.symbol_tables.enter_block()
        
        # Visit declarations
        for decl in node.declarations:
            self.visit(decl)
        
        # Visit compound statement
        self.visit(node.compound_statement)
        
        # Exit scope
        self.symbol_tables.exit_block()
        
        return None
    
    def visit_CompoundStatementNode(self, node: CompoundStatementNode):
        for stmt in node.statements:
            self.visit(stmt)
        return None
    
    def visit_VarDeclNode(self, node: VarDeclNode):
        var_type = self.resolve_type(node.type_name)
        
        for var_name in node.names:
            existing = self.symbol_tables.lookup(var_name)
            if existing is not None:
                entry = self.symbol_tables.tab[existing]
                if entry.lev == self.symbol_tables.level:
                    self.error(f"Variable '{var_name}' already declared in this scope", node)
                    continue
            
            # Add to symbol table
            idx = self.symbol_tables.add_symbol(
                identifier=var_name,
                obj=ObjKind.VARIABLE,
                typ=var_type,
                nrm=1  # normal variable
            )
            if self.symbol_tables.level < len(self.symbol_tables.btab):
                self.symbol_tables.btab[self.symbol_tables.level].vsze += 1
        
        node.type = var_type
        node.scope_level = self.symbol_tables.level
        
        return var_type
    
    def visit_ConstDeclNode(self, node: ConstDeclNode):
        value_type = self.visit(node.value)
        
        existing = self.symbol_tables.lookup(node.name)
        if existing is not None:
            entry = self.symbol_tables.tab[existing]
            if entry.lev == self.symbol_tables.level:
                self.error(f"Constant '{node.name}' already declared in this scope", node)
                return value_type
        
        # Add to symbol table
        idx = self.symbol_tables.add_symbol(
            identifier=node.name,
            obj=ObjKind.CONSTANT,
            typ=value_type,
            nrm=1  # normal constant
        )
        
        node.type = value_type
        node.tab_index = idx
        
        return value_type
    
    def visit_TypeDeclNode(self, node: TypeDeclNode):
        resolved_type = self.resolve_type(node.type_name)
        
        idx = self.symbol_tables.add_symbol(
            identifier=node.name,
            obj=ObjKind.TYPE,
            typ=resolved_type
        )

        
        node.type = resolved_type
        node.tab_index = idx
        
        return resolved_type
    
    def visit_ProcedureDeclNode(self, node: ProcedureDeclNode):
        
        idx = self.symbol_tables.add_symbol(
            identifier=node.name,
            obj=ObjKind.PROCEDURE,
            typ=TypeKind.UNKNOWN
        )
        
        self.symbol_tables.enter_block()
        
        for param in node.params:
            self.visit(param)
        
        self.visit(node.block)
        
        self.symbol_tables.exit_block()
        
        node.tab_index = idx
        node.scope_level = self.symbol_tables.level
        
        return None
    
    def visit_FunctionDeclNode(self, node: FunctionDeclNode):
        
        return_type = self.resolve_type(node.return_type)

        idx = self.symbol_tables.add_symbol(
            identifier=node.name,
            obj=ObjKind.FUNCTION,
            typ=return_type
        )
        
        old_func = self.current_function
        self.current_function = (node.name, return_type)

        self.symbol_tables.enter_block()
        
        for param in node.params:
            self.visit(param)
        
        self.visit(node.block)
        
        self.symbol_tables.exit_block()

        self.current_function = old_func
        
        node.type = return_type
        node.tab_index = idx
        node.scope_level = self.symbol_tables.level
        
        return return_type
    
    def visit_ParameterNode(self, node: ParameterNode):
        param_type = self.resolve_type(node.type_name)
        
        for param_name in node.names:
            idx = self.symbol_tables.add_symbol(
                identifier=param_name,
                obj=ObjKind.VARIABLE,
                typ=param_type,
                nrm=0  # parameter (by reference)
            )
        
        node.type = param_type
        return param_type
    
    def visit_AssignNode(self, node: AssignNode):
        target_type = self.visit(node.target)
        
        value_type = self.visit(node.value)
        
        if not self.check_type_compatibility(target_type, value_type):
            self.error(
                f"Type mismatch in assignment: cannot assign {value_type} to {target_type}", node
            )
        
        node.type = TypeKind.UNKNOWN 
        
        return None
    
    def visit_IfNode(self, node: IfNode):
        cond_type = self.visit(node.condition)
        if cond_type != TypeKind.BOOLEAN:
            self.error(f"If condition must be boolean, got {cond_type}", node)
            
        self.visit(node.then_statement)
        
        if node.else_statement:
            self.visit(node.else_statement)
        
        return None
    
    def visit_WhileNode(self, node: WhileNode):
        cond_type = self.visit(node.condition)
        if cond_type != TypeKind.BOOLEAN:
            self.error(f"While condition must be boolean, got {cond_type}", node)

        self.visit(node.body)
        
        return None
    
    def visit_ForNode(self, node: ForNode):
        var_type = self.visit(node.var)
        if var_type != TypeKind.INTEGER:
            self.error(f"For loop variable must be integer, got {var_type}", node)
        
        start_type = self.visit(node.start_expr)
        end_type = self.visit(node.end_expr)
        
        if start_type != TypeKind.INTEGER:
            self.error(f"For loop start expression must be integer, got {start_type}", node)
        if end_type != TypeKind.INTEGER:
            self.error(f"For loop end expression must be integer, got {end_type}", node)
        
        # Visit body
        self.visit(node.body)
        
        return None
    
    def visit_ProcedureFunctionCallNode(self, node: ProcedureFunctionCallNode):
        idx = self.symbol_tables.lookup(node.name)
        
        if idx is None:
            self.error(f"Undeclared procedure/function '{node.name}'", node)
            node.type = TypeKind.UNKNOWN
            return TypeKind.UNKNOWN
        
        entry = self.symbol_tables.tab[idx]
        
        if entry.obj not in (ObjKind.PROCEDURE, ObjKind.FUNCTION):
            self.error(f"'{node.name}' is not a procedure or function", node)
            return TypeKind.UNKNOWN
        
        arg_types = []
        for arg in node.arguments:
            arg_type = self.visit(arg)
            arg_types.append(arg_type)
        
        node.tab_index = idx
        node.type = entry.type  
        
        print(f"  [CALL] {entry.obj} '{node.name}' with {len(arg_types)} arguments")
        
        return entry.type
    
    def visit_BinOpNode(self, node: BinOpNode):
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)
        
        result_type = self.get_binop_result_type(node.op, left_type, right_type)
        
        node.type = result_type
        
        return result_type
    
    def visit_UnaryOpNode(self, node: UnaryOpNode):
        operand_type = self.visit(node.operand)
        
        if node.op in ('+', '-'):
            if operand_type not in (TypeKind.INTEGER, TypeKind.REAL):
                self.error(f"Unary {node.op} requires numeric operand, got {operand_type}", node)
                result_type = TypeKind.UNKNOWN
            else:
                result_type = operand_type
        
        elif node.op == 'tidak':  # NOT
            if operand_type != TypeKind.BOOLEAN:
                self.error(f"NOT operator requires boolean operand, got {operand_type}", node)
                result_type = TypeKind.UNKNOWN
            else:
                result_type = TypeKind.BOOLEAN
        else:
            self.error(f"Unknown unary operator '{node.op}'", node)
            result_type = TypeKind.UNKNOWN
        
        node.type = result_type
        return result_type
    
    def visit_VarNode(self, node: VarNode):
        idx = self.symbol_tables.lookup(node.name)
        
        if idx is None:
            self.error(f"Undeclared identifier '{node.name}'", node)
            node.type = TypeKind.UNKNOWN
            node.tab_index = None
            return TypeKind.UNKNOWN
        
        entry = self.symbol_tables.tab[idx]
        
        node.type = entry.type
        node.tab_index = idx
        node.scope_level = entry.lev
        
        return entry.type
    
    def visit_NumberNode(self, node: NumberNode):
        # Type already set in __init__ of NumberNode
        return node.type
    
    def visit_StringNode(self, node: StringNode):
        return node.type  # 'string'
    
    def visit_CharNode(self, node: CharNode):
        return node.type  # 'char'
    
    def visit_ArrayAccessNode(self, node: ArrayAccessNode):
        array_type = self.visit(node.array_var)
        
        if not isinstance(array_type, str) or not array_type.startswith('array'):
            self.error(f"'{node.array_var.name}' is not an array", node)
            return TypeKind.UNKNOWN
        
        index_type = self.visit(node.index_expression)
        
        if index_type != TypeKind.INTEGER:
            self.error(f"Array index must be integer, got {index_type}", node)
        
        if array_type.startswith("array of "):
            element_type = array_type[len("array of "):]
            node.type = element_type
            return element_type
        else:
            node.type = TypeKind.UNKNOWN
            return TypeKind.UNKNOWN
    
    def visit_NoOpNode(self, node):
        return None
    
    
    def resolve_type(self, type_name):
        if isinstance(type_name, str):
            # Built-in types
            if type_name in ('integer', 'real', 'boolean', 'char', 'string'):
                return type_name
            
            idx = self.symbol_tables.lookup(type_name)
            if idx is not None:
                entry = self.symbol_tables.tab[idx]
                if entry.obj == ObjKind.TYPE:
                    return entry.type
            
            # Create a dummy node for error reporting
            dummy_node = type('',(object,),{'line':0,'column':0})()
            self.error(f"Unknown type '{type_name}'", dummy_node)
            return TypeKind.UNKNOWN
        
        elif isinstance(type_name, ArrayTypeNode):
            element_type = self.resolve_type(type_name.element_type)
            return f"array of {element_type}"
        
        else:
            return TypeKind.UNKNOWN
    
    def check_type_compatibility(self, type1, type2):
        if type1 == TypeKind.UNKNOWN or type2 == TypeKind.UNKNOWN:
            return True  # Don't cascade errors
        
        if type1 == type2:
            return True
        
        if (type1 == TypeKind.REAL and type2 == TypeKind.INTEGER):
            return True
        
        return False
    
    def get_binop_result_type(self, op, left_type, right_type):
        if op in ('+', '-', '*', '/'):
            if left_type == TypeKind.UNKNOWN or right_type == TypeKind.UNKNOWN:
                return TypeKind.UNKNOWN
            
            if left_type not in (TypeKind.INTEGER, TypeKind.REAL):
                dummy_node = type('',(object,),{'line':0,'column':0})()
                self.error(f"Arithmetic operator '{op}' requires numeric operands, got {left_type}", dummy_node)
                return TypeKind.UNKNOWN
            
            if right_type not in (TypeKind.INTEGER, TypeKind.REAL):
                dummy_node = type('',(object,),{'line':0,'column':0})()
                self.error(f"Arithmetic operator '{op}' requires numeric operands, got {right_type}", dummy_node)
                return TypeKind.UNKNOWN
            
            # Result type promotion
            if left_type == TypeKind.REAL or right_type == TypeKind.REAL:
                return TypeKind.REAL
            else:
                return TypeKind.INTEGER
        
        elif op in ('bagi', 'mod'):
            if left_type != TypeKind.INTEGER or right_type != TypeKind.INTEGER:
                dummy_node = type('',(object,),{'line':0,'column':0})()
                self.error(f"Operator '{op}' requires integer operands", dummy_node)
                return TypeKind.UNKNOWN
            return TypeKind.INTEGER
        
        elif op in ('dan', 'atau'):
            if left_type != TypeKind.BOOLEAN:
                dummy_node = type('',(object,),{'line':0,'column':0})()
                self.error(f"Logical operator '{op}' requires boolean operands, got {left_type}", dummy_node)
            if right_type != TypeKind.BOOLEAN:
                dummy_node = type('',(object,),{'line':0,'column':0})()
                self.error(f"Logical operator '{op}' requires boolean operands, got {right_type}", dummy_node)
            return TypeKind.BOOLEAN
        
        elif op in ('=', '<>', '<', '>', '<=', '>='):
            if left_type == TypeKind.UNKNOWN or right_type == TypeKind.UNKNOWN:
                return TypeKind.BOOLEAN
            
            if not self.check_type_compatibility(left_type, right_type):
                dummy_node = type('',(object,),{'line':0,'column':0})()
                self.error(f"Cannot compare {left_type} with {right_type}", dummy_node)
            
            return TypeKind.BOOLEAN
        
        else:
            dummy_node = type('',(object,),{'line':0,'column':0})()
            self.error(f"Unknown binary operator '{op}'", dummy_node)
            return TypeKind.UNKNOWN
    
    def print_symbol_table(self):
        print("\n=== SYMBOL TABLE (TAB) ===")
        print(f"{'Idx':<5} {'ID':<15} {'Obj':<12} {'Type':<10} {'Ref':<5} {'Nrm':<5} {'Lev':<5} {'Adr':<5} {'Link':<5}")
        print("-" * 75)
        for i, entry in enumerate(self.symbol_tables.tab):
            print(f"{i:<5} {entry.identifier:<15} {entry.obj:<12} {entry.type:<10} {entry.ref:<5} {entry.nrm:<5} {entry.lev:<5} {entry.adr:<5} {entry.link:<5}")
        
        print("\n=== BLOCK TABLE (BTAB) ===")
        print(f"{'Idx':<5} {'Last':<6} {'Lpar':<6} {'Psze':<6} {'Vsze':<6}")
        print("-" * 35)
        for i, block in enumerate(self.symbol_tables.btab):
            print(f"{i:<5} {block.last:<6} {block.lpar:<6} {block.psze:<6} {block.vsze:<6}")
        
        print("\n=== ARRAY TABLE (ATAB) ===")
        if len(self.symbol_tables.atab) == 0:
            print("(empty - no arrays declared)")
        else:
            print(f"{'Idx':<5} {'Xtyp':<6} {'Etyp':<10} {'Eref':<6} {'Low':<6} {'High':<6} {'Elsz':<6} {'Size':<6}")
            print("-" * 55)
            for i, arr in enumerate(self.symbol_tables.atab):
                print(f"{i:<5} {arr.xtyp:<6} {arr.etyp:<10} {arr.eref:<6} {arr.low:<6} {arr.high:<6} {arr.elsz:<6} {arr.size:<6}")
        
        # Debugging
        # print("\n=== DISPLAY (Lexical Level Pointers) ===")
        # print(f"Level -> Tab Index (head of linked list)")
        # for level, idx in enumerate(self.symbol_tables.display):
        #     print(f"  {level} -> {idx}")
        
        # print("\n=== LINKED LIST TRAVERSAL (Level 0 - Global Block) ===")
        # idx = self.symbol_tables.display[0]
        # if idx == 0:
        #     print("  (empty linked list at level 0)")
        # else:
        #     print("  Traversal order (following links):")
        #     count = 0
        #     while idx != 0 and count < 100:
        #         entry = self.symbol_tables.tab[idx]
        #         print(f"    [{idx}] {entry.identifier} ({entry.obj}) -> link={entry.link}")
        #         idx = entry.link
        #         count += 1