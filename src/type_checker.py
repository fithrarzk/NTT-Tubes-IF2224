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
        # Masukkan nama program ke tab dengan linking ke global block
        prev_last = self.symbol_tables.btab[0].last
        
        prog_entry = SymbolTableEntry(
            identifier=node.name,
            link=prev_last,  # Link ke entry sebelumnya di global block
            obj="program",
            typ=TypeKind.UNKNOWN,
            ref=0,
            nrm=1,
            lev=0,
            adr=0
        )
        self.symbol_tables.tab.append(prog_entry)
        prog_idx_1based = len(self.symbol_tables.tab)
        
        # Update btab[0].last untuk menunjuk ke program entry
        self.symbol_tables.btab[0].last = prog_idx_1based
        
        # Process declarations (variabel global)
        for decl in node.declarations:
            self.visit(decl)

        self.symbol_tables.enter_block()  # level = 1, btab[1] dibuat
        
        if node.block:
            self.visit(node.block)
        
        self.symbol_tables.exit_block()  # kembali ke level 0

        node.scope_level = 0

        return node
    
    def visit_BlockNode(self, node: BlockNode):
        self.symbol_tables.enter_block()
        
        # Visit declarations dalam block ini
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
        
        # Check if array type
        atab_ref = 0
        actual_type = var_type
        if isinstance(var_type, tuple):
            actual_type, atab_ref = var_type
        
        for var_name in node.names:
            existing = self.symbol_tables.lookup(var_name)
            if existing is not None:
                entry = self.symbol_tables.tab[existing]
                if entry.lev == self.symbol_tables.level:
                    self.error(f"Variable '{var_name}' already declared in this scope", node)
                    continue
            
            # Add to symbol table dengan linking ke block chain
            idx = self.symbol_tables.add_symbol(
                identifier=var_name,
                obj=ObjKind.VARIABLE,
                typ=actual_type,
                ref=atab_ref,
                nrm=1  # normal variable
            )
            
            # Update vsze (variable size) di btab untuk block saat ini
            current_block_idx = self.symbol_tables.display[self.symbol_tables.level]
            if current_block_idx < len(self.symbol_tables.btab):
                self.symbol_tables.btab[current_block_idx].vsze += 1
        
        node.type = actual_type
        node.scope_level = self.symbol_tables.level
        
        return actual_type
    
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
                f"Type mismatch in assignment: cannot assign {TypeKind.to_string(value_type)} to {TypeKind.to_string(target_type)}", node
            )
        
        node.type = TypeKind.UNKNOWN 
        
        return None
    
    def visit_IfNode(self, node: IfNode):
        cond_type = self.visit(node.condition)
        if cond_type != TypeKind.BOOLEAN:
            self.error(f"If condition must be boolean, got {TypeKind.to_string(cond_type)}", node)
            
        self.visit(node.then_statement)
        
        if node.else_statement:
            self.visit(node.else_statement)
        
        return None
    
    def visit_WhileNode(self, node: WhileNode):
        cond_type = self.visit(node.condition)
        if cond_type != TypeKind.BOOLEAN:
            self.error(f"While condition must be boolean, got {TypeKind.to_string(cond_type)}", node)

        self.visit(node.body)
        
        return None
    
    def visit_ForNode(self, node: ForNode):
        var_type = self.visit(node.var)
        if var_type != TypeKind.INTEGER:
            self.error(f"For loop variable must be integer, got {TypeKind.to_string(var_type)}", node)
        
        start_type = self.visit(node.start_expr)
        end_type = self.visit(node.end_expr)
        
        if start_type != TypeKind.INTEGER:
            self.error(f"For loop start expression must be integer, got {TypeKind.to_string(start_type)}", node)
        if end_type != TypeKind.INTEGER:
            self.error(f"For loop end expression must be integer, got {TypeKind.to_string(end_type)}", node)
        
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
                self.error(f"Unary {node.op} requires numeric operand, got {TypeKind.to_string(operand_type)}", node)
                result_type = TypeKind.UNKNOWN
            else:
                result_type = operand_type
        
        elif node.op == 'tidak':  # NOT
            if operand_type != TypeKind.BOOLEAN:
                self.error(f"NOT operator requires boolean operand, got {TypeKind.to_string(operand_type)}", node)
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
        # Get the array variable's type
        array_var_idx = self.symbol_tables.lookup(node.array_var.name)
        
        if array_var_idx is None:
            self.error(f"Undeclared array '{node.array_var.name}'", node)
            return TypeKind.UNKNOWN
        
        array_entry = self.symbol_tables.tab[array_var_idx]
        
        # Check if it's actually an array
        if array_entry.type != TypeKind.ARRAY:
            self.error(f"'{node.array_var.name}' is not an array (type={array_entry.type})", node)
            return TypeKind.UNKNOWN
        
        # Check index type
        index_type = self.visit(node.index_expression)
        if index_type != TypeKind.INTEGER:
            self.error(f"Array index must be integer, got {TypeKind.to_string(index_type)}", node)
        
        # Look up in atab to get element type
        atab_index = array_entry.ref
        if atab_index < len(self.symbol_tables.atab):
            atab_entry = self.symbol_tables.atab[atab_index]
            element_type = atab_entry.etyp
            
            node.type = element_type
            return element_type
        else:
            self.error(f"Invalid array table reference for '{node.array_var.name}'", node)
            node.type = TypeKind.UNKNOWN
            return TypeKind.UNKNOWN
    
    def visit_NoOpNode(self, node):
        return None
    
    
    def resolve_type(self, type_name):
        if isinstance(type_name, str):
            # Built-in types
            type_map = {
                'integer': TypeKind.INTEGER,
                'real': TypeKind.REAL,
                'boolean': TypeKind.BOOLEAN,
                'char': TypeKind.CHAR,
                'string': TypeKind.STRING
            }
            
            if type_name.lower() in type_map:
                return type_map[type_name.lower()]
            
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
            
            if hasattr(type_name.index_range, 'low') and hasattr(type_name.index_range, 'high'):
                low_node = type_name.index_range.low
                high_node = type_name.index_range.high
                
                # Extract integer values from NumberNode
                if isinstance(low_node, NumberNode):
                    low = int(low_node.value)
                else:
                    low = low_node
                
                if isinstance(high_node, NumberNode):
                    high = int(high_node.value)
                else:
                    high = high_node
                
                # Calculate array size
                element_size = 1  # Simplified
                
                # Add to atab and return the index
                atab_index = self.symbol_tables.add_array_type(
                    xtyp=TypeKind.ARRAY, 
                    etyp=element_type,   
                    eref=0,            
                    low=low,              
                    high=high,             
                    elsz=element_size
                )
                
                return (TypeKind.ARRAY, atab_index)
            else:
                dummy_node = type('',(object,),{'line':0,'column':0})()
                self.error(f"Invalid array index range", dummy_node)
                return TypeKind.UNKNOWN
        
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
                self.error(f"Arithmetic operator '{op}' requires numeric operands, got {TypeKind.to_string(left_type)}", dummy_node)
                return TypeKind.UNKNOWN
            
            if right_type not in (TypeKind.INTEGER, TypeKind.REAL):
                dummy_node = type('',(object,),{'line':0,'column':0})()
                self.error(f"Arithmetic operator '{op}' requires numeric operands, got {TypeKind.to_string(right_type)}", dummy_node)
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
                self.error(f"Logical operator '{op}' requires boolean operands, got {TypeKind.to_string(left_type)}", dummy_node)
            if right_type != TypeKind.BOOLEAN:
                dummy_node = type('',(object,),{'line':0,'column':0})()
                self.error(f"Logical operator '{op}' requires boolean operands, got {TypeKind.to_string(right_type)}", dummy_node)
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
        print(f"{'Idx':<5} {'ID':<15} {'Obj':<12} {'Type':<15} {'Ref':<5} {'Nrm':<5} {'Lev':<5} {'Adr':<5} {'Link':<5}")
        print("-" * 85)
        for i, entry in enumerate(self.symbol_tables.tab):
            # Convert link from 1-based to 0-based for display (0 stays 0, n becomes n-1)
            link_0based = entry.link - 1 if entry.link > 0 else 0
            print(f"{i:<5} {entry.identifier:<15} {entry.obj:<12} {entry.type:<5} {entry.ref:<5} {entry.nrm:<5} {entry.lev:<5} {entry.adr:<5} {link_0based:<5}")

        print("\n=== BLOCK TABLE (BTAB) ===")
        print(f"{'Idx':<5} {'Last':<6} {'Lpar':<6} {'Psze':<6} {'Vsze':<6}")
        print("-" * 35)
        for i, block in enumerate(self.symbol_tables.btab):
            # Convert last from 1-based to 0-based for display (0 stays 0, n becomes n-1)
            last_0based = block.last - 1 if block.last > 0 else 0
            print(f"{i:<5} {last_0based:<6} {block.lpar:<6} {block.psze:<6} {block.vsze:<6}")
        
        print("\n=== ARRAY TABLE (ATAB) ===")
        if len(self.symbol_tables.atab) == 0:
            print("(empty - no arrays declared)")
        else:
            print(f"{'Idx':<5} {'Xtyp':<6} {'Etyp':<10} {'Eref':<6} {'Low':<6} {'High':<6} {'Elsz':<6} {'Size':<6}")
            print("-" * 55)
            for i, arr in enumerate(self.symbol_tables.atab):
                print(f"{i:<5} {arr.xtyp:<6} {arr.etyp:<10} {arr.eref:<6} {arr.low:<6} {arr.high:<6} {arr.elsz:<6} {arr.size:<6}")
        