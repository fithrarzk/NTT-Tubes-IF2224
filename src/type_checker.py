from .ast_nodes import *
from .symbol_table import *

class TypeChecker:
    def __init__(self, symbol_tables: SymbolTables):
        self.symbol_tables = symbol_tables
        self.current_function = None

    def _node_pos(self, node: ASTNode):
        # safety: beberapa node mungkin None atau tanpa atribut line/column
        line = getattr(node, "line", 0) if node is not None else 0
        column = getattr(node, "column", 0) if node is not None else 0
        return line, column

    def error(self, message: str, node: ASTNode):
        line, col = self._node_pos(node)
        raise TypeError(f"Type Error at line {line}, column {col}: {message}")
    
    def visit(self, node: ASTNode):
        if node is None:
            return None
        
        method_name = f'visit_{node.__class__.__name__}'
        visitor = getattr(self, method_name, self.generic_visit)

        result_type = visitor(node)
        # hanya set node.type jika visitor mengembalikan tipe (int) atau tuple untuk array
        if result_type is not None and not isinstance(result_type, ASTNode):
            node.type = result_type 

        return result_type
    
    def generic_visit(self, node: ASTNode):
        # jika tidak ada implementasi visitor khusus -> error semantic
        self.error(f"No visit method for {node.__class__.__name__}", node)
        return TypeKind.UNKNOWN
    
    def visit_ProgramNode(self, node: ProgramNode):
        """
        Program:
         - level 0: deklarasi dan entry program
         - level 1: body (compound statement)
        """
        # add program name ke symbol table (level saat ini harus 0 karena SymbolTables sudah enter_block di ctor)
        prog_idx = self.symbol_tables.add_symbol(
            identifier=node.name,
            obj=ObjKind.PROGRAM,
            typ=TypeKind.UNKNOWN,
            nrm=1
        )
        node.tab_index = prog_idx
        node.scope_level = self.symbol_tables.level  # biasanya 0

        # proses deklarasi di level 0
        for decl in node.declarations:
            self.visit(decl)
        
        # enter block untuk main/body (level 1)
        self.symbol_tables.enter_block()
        if node.block:
            self.visit(node.block)
        self.symbol_tables.exit_block()

        return None  # visitor tidak mengembalikan tipe (bukan expression)
    
    def visit_BlockNode(self, node: BlockNode):
        self.symbol_tables.enter_block()
        for decl in node.declarations:
            self.visit(decl)
        if node.compound_statement:
            self.visit(node.compound_statement)
        self.symbol_tables.exit_block()
        return None
    
    def visit_CompoundStatementNode(self, node: CompoundStatementNode):
        for stmt in node.statements:
            self.visit(stmt)
        return None
    
    def visit_VarDeclNode(self, node: VarDeclNode):
        # resolve type_name -> bisa int kode TypeKind atau (ARRAY, atab_index)
        var_type = self.resolve_type(node.type_name)
        
        atab_ref = 0
        actual_type = var_type
        if isinstance(var_type, tuple):
            actual_type, atab_ref = var_type
        
        # dapatkan block index (btab index) dari display
        bidx = self.symbol_tables.display[self.symbol_tables.level]
        current_vsze = self.symbol_tables.btab[bidx].vsze
        
        for var_name in node.names:
            # cek redeclare di block saat ini
            existing = self.symbol_tables.find_in_current_block(var_name)
            if existing is not None:
                self.error(f"Variable '{var_name}' already declared in this scope", node)
                continue

            adr = current_vsze
            self.symbol_tables.add_symbol(
                identifier=var_name,
                obj=ObjKind.VARIABLE,
                typ=actual_type,
                ref=atab_ref,
                nrm=1,
                adr=adr
            )
            current_vsze += 1

        # update vsze pada block
        self.symbol_tables.btab[bidx].vsze = current_vsze

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

        idx = self.symbol_tables.add_symbol(
            identifier=node.name,
            obj=ObjKind.CONSTANT,
            typ=value_type,
            nrm=1
        )
        node.type = value_type
        node.tab_index = idx
        return value_type

    def visit_TypeDeclNode(self, node: TypeDeclNode):
        resolved = self.resolve_type(node.type_name)
        idx = self.symbol_tables.add_symbol(
            identifier=node.name,
            obj=ObjKind.TYPE,
            typ=resolved
        )
        node.type = resolved
        node.tab_index = idx
        return resolved

    def visit_ProcedureDeclNode(self, node: ProcedureDeclNode):
        idx = self.symbol_tables.add_symbol(
            identifier=node.name,
            obj=ObjKind.PROCEDURE,
            typ=TypeKind.UNKNOWN
        )
        node.tab_index = idx

        # masukkan param & body pada block baru
        self.symbol_tables.enter_block()
        param_count = 0
        for param in node.params:
            self.visit(param)
            param_count += len(param.names) if hasattr(param, "names") else 0

        # update psze pada block entry
        bidx = self.symbol_tables.display[self.symbol_tables.level]
        self.symbol_tables.btab[bidx].psze = param_count

        if node.block:
            self.visit(node.block)
        self.symbol_tables.exit_block()

        node.scope_level = self.symbol_tables.level
        return None

    def visit_FunctionDeclNode(self, node: FunctionDeclNode):
        return_type = self.resolve_type(node.return_type)
        idx = self.symbol_tables.add_symbol(
            identifier=node.name,
            obj=ObjKind.FUNCTION,
            typ=return_type
        )
        node.tab_index = idx

        old_func = self.current_function
        self.current_function = (node.name, return_type)

        self.symbol_tables.enter_block()
        for param in node.params:
            self.visit(param)
        if node.block:
            self.visit(node.block)
        self.symbol_tables.exit_block()

        self.current_function = old_func
        node.type = return_type
        node.scope_level = self.symbol_tables.level
        return return_type

    def visit_ParameterNode(self, node: ParameterNode):
        param_type = self.resolve_type(node.type_name)
        for pname in node.names:
            self.symbol_tables.add_symbol(
                identifier=pname,
                obj=ObjKind.PARAMETER,
                typ=param_type,
                nrm=0  # parameter by ref (konvensi)
            )
        node.type = param_type
        return param_type

    def visit_AssignNode(self, node: AssignNode):
        # left harus VarNode atau ArrayAccess
        target_type = self.visit(node.target)
        value_type = self.visit(node.value)

        if target_type is None:
            self.error("Left-hand side of assignment has no type", node)

        # gunakan kompatibilitas tipe
        if not self.check_type_compatibility(target_type, value_type):
            self.error(f"Type mismatch in assignment: cannot assign {TypeKind.to_string(value_type)} to {TypeKind.to_string(target_type)}", node)

        node.type = target_type
        return target_type

    def visit_IfNode(self, node: IfNode):
        cond_type = self.visit(node.condition)
        if cond_type != TypeKind.BOOLEAN:
            self.error(f"If condition must be boolean, got {TypeKind.to_string(cond_type)}", node)
        if node.then_statement:
            self.visit(node.then_statement)
        if node.else_statement:
            self.visit(node.else_statement)
        return None

    def visit_WhileNode(self, node: WhileNode):
        cond_type = self.visit(node.condition)
        if cond_type != TypeKind.BOOLEAN:
            self.error(f"While condition must be boolean, got {TypeKind.to_string(cond_type)}", node)
        if node.body:
            self.visit(node.body)
        return None

    def visit_ForNode(self, node: ForNode):
        # var harus VarNode yang terdeklarasi
        var_type = self.visit(node.var)
        if var_type != TypeKind.INTEGER:
            self.error(f"For loop variable must be integer, got {TypeKind.to_string(var_type)}", node)

        start_type = self.visit(node.start_expr)
        end_type = self.visit(node.end_expr)
        if start_type != TypeKind.INTEGER:
            self.error(f"For loop start expression must be integer, got {TypeKind.to_string(start_type)}", node)
        if end_type != TypeKind.INTEGER:
            self.error(f"For loop end expression must be integer, got {TypeKind.to_string(end_type)}", node)

        if node.body:
            self.visit(node.body)
        return None

    def visit_ProcedureFunctionCallNode(self, node: ProcedureFunctionCallNode):
        # node.name adalah string
        idx = self.symbol_tables.lookup(node.name)
        if idx is None:
            self.error(f"Undeclared procedure/function '{node.name}'", node)
            return TypeKind.UNKNOWN

        entry = self.symbol_tables.tab[idx]
        if entry.obj not in (ObjKind.PROCEDURE, ObjKind.FUNCTION):
            self.error(f"'{node.name}' is not a procedure or function", node)
            return TypeKind.UNKNOWN

        # visit each arg
        arg_types = []
        for arg in node.arguments:
            arg_types.append(self.visit(arg))

        node.tab_index = idx
        node.type = entry.type
        return entry.type

    def visit_BinOpNode(self, node: BinOpNode):
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)

        # gunakan helper yang sudah ada untuk konsistensi dan validasi
        result_type = self.get_binop_result_type(node.op, left_type, right_type)
        node.type = result_type
        return result_type

    def visit_UnaryOpNode(self, node: UnaryOpNode):
        operand_type = self.visit(node.operand)
        if node.op in ('+', '-'):
            if operand_type not in (TypeKind.INTEGER, TypeKind.REAL):
                self.error(f"Unary {node.op} requires numeric operand, got {TypeKind.to_string(operand_type)}", node)
                return TypeKind.UNKNOWN
            node.type = operand_type
            return operand_type
        elif node.op in ('tidak', 'not'):
            if operand_type != TypeKind.BOOLEAN:
                self.error(f"NOT operator requires boolean operand, got {TypeKind.to_string(operand_type)}", node)
                return TypeKind.UNKNOWN
            node.type = TypeKind.BOOLEAN
            return TypeKind.BOOLEAN
        else:
            self.error(f"Unknown unary operator '{node.op}'", node)
            return TypeKind.UNKNOWN

    def visit_VarNode(self, node: VarNode):
        idx = self.symbol_tables.lookup(node.name)
        if idx is None:
            self.error(f"Undeclared identifier '{node.name}'", node)
            node.tab_index = None
            node.type = TypeKind.UNKNOWN
            return TypeKind.UNKNOWN

        entry = self.symbol_tables.tab[idx]
        node.type = entry.type
        node.tab_index = idx
        node.scope_level = entry.lev
        return entry.type

    def visit_NumberNode(self, node: NumberNode):
        # node.value bisa str atau int/float; NumberNode ctor biasanya sudah set type
        if isinstance(node.value, int):
            node.type = TypeKind.INTEGER
            return TypeKind.INTEGER
        if isinstance(node.value, str):
            if '.' in node.value or 'e' in node.value.lower():
                node.type = TypeKind.REAL
                return TypeKind.REAL
            else:
                node.type = TypeKind.INTEGER
                return TypeKind.INTEGER
        # fallback
        node.type = TypeKind.REAL
        return TypeKind.REAL

    def visit_StringNode(self, node: StringNode):
        node.type = TypeKind.STRING
        return TypeKind.STRING

    def visit_CharNode(self, node: CharNode):
        node.type = TypeKind.CHAR
        return TypeKind.CHAR

    def visit_ArrayAccessNode(self, node: ArrayAccessNode):
        # cari variable array
        array_idx = self.symbol_tables.lookup(node.array_var.name)
        if array_idx is None:
            self.error(f"Undeclared array '{node.array_var.name}'", node)
            return TypeKind.UNKNOWN

        entry = self.symbol_tables.tab[array_idx]
        if entry.type != TypeKind.ARRAY:
            self.error(f"'{node.array_var.name}' is not an array (type={entry.type})", node)
            return TypeKind.UNKNOWN

        index_type = self.visit(node.index_expression)
        if index_type != TypeKind.INTEGER:
            self.error(f"Array index must be integer, got {TypeKind.to_string(index_type)}", node)

        atab_index = entry.ref
        if not (0 <= atab_index < len(self.symbol_tables.atab)):
            self.error(f"Invalid array table reference for '{node.array_var.name}'", node)
            node.type = TypeKind.UNKNOWN
            return TypeKind.UNKNOWN

        atab_entry = self.symbol_tables.atab[atab_index]
        node.type = atab_entry.etyp
        return atab_entry.etyp

    def visit_NoOpNode(self, node: NoOpNode):
        return None

    # -------------------------
    # helpers
    # -------------------------
    def resolve_type(self, type_name):
        # jika string nama tipe (built-in atau typedef)
        if isinstance(type_name, str):
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

            dummy = type('', (object,), {'line':0,'column':0})()
            self.error(f"Unknown type '{type_name}'", dummy)
            return TypeKind.UNKNOWN

        # array type node
        if isinstance(type_name, ArrayTypeNode):
            elem_type = self.resolve_type(type_name.element_type)
            if hasattr(type_name.index_range, 'low') and hasattr(type_name.index_range, 'high'):
                low_node = type_name.index_range.low
                high_node = type_name.index_range.high

                if isinstance(low_node, NumberNode):
                    low = int(low_node.value)
                else:
                    # if non-literal, error (Pascal-S spec: range should be const int)
                    low = None

                if isinstance(high_node, NumberNode):
                    high = int(high_node.value)
                else:
                    high = None

                if low is None or high is None:
                    dummy = type('', (object,), {'line':0,'column':0})()
                    self.error("Array index range must be integer constants", dummy)
                    return TypeKind.UNKNOWN

                element_size = 1
                atab_idx = self.symbol_tables.add_array_type(
                    xtyp=TypeKind.ARRAY,
                    etyp=elem_type,
                    eref=0,
                    low=low,
                    high=high,
                    elsz=element_size
                )
                return (TypeKind.ARRAY, atab_idx)
            else:
                dummy = type('', (object,), {'line':0,'column':0})()
                self.error("Invalid array index range", dummy)
                return TypeKind.UNKNOWN

        return TypeKind.UNKNOWN

    def check_type_compatibility(self, type1, type2):
        # if unknown, skip cascading error
        if type1 == TypeKind.UNKNOWN or type2 == TypeKind.UNKNOWN:
            return True
        if type1 == type2:
            return True
        # implicit promotion integer -> real allowed
        if type1 == TypeKind.REAL and type2 == TypeKind.INTEGER:
            return True
        return False

    def get_binop_result_type(self, op, left_type, right_type):
        # reuse helper yang ada di file lama tapi dengan pengecekan lebih konsisten
        if op in ('+', '-', '*', '/'):
            # require numeric operands
            if left_type not in (TypeKind.INTEGER, TypeKind.REAL) or right_type not in (TypeKind.INTEGER, TypeKind.REAL):
                dummy = type('',(object,),{'line':0,'column':0})()
                self.error(f"Arithmetic operator '{op}' requires numeric operands", dummy)
                return TypeKind.UNKNOWN
            if left_type == TypeKind.REAL or right_type == TypeKind.REAL:
                return TypeKind.REAL
            return TypeKind.INTEGER

        if op in ('bagi', 'mod'):
            # integer-only
            if left_type != TypeKind.INTEGER or right_type != TypeKind.INTEGER:
                dummy = type('',(object,),{'line':0,'column':0})()
                self.error(f"Operator '{op}' requires integer operands", dummy)
                return TypeKind.UNKNOWN
            return TypeKind.INTEGER

        if op in ('dan', 'atau'):
            if left_type != TypeKind.BOOLEAN or right_type != TypeKind.BOOLEAN:
                dummy = type('',(object,),{'line':0,'column':0})()
                self.error(f"Logical operator '{op}' requires boolean operands", dummy)
                return TypeKind.UNKNOWN
            return TypeKind.BOOLEAN

        if op in ('=', '<>', '<', '>', '<=', '>='):
            # allow comparison if compatible (int<->real allowed)
            if not self.check_type_compatibility(left_type, right_type):
                dummy = type('',(object,),{'line':0,'column':0})()
                self.error(f"Cannot compare {TypeKind.to_string(left_type)} with {TypeKind.to_string(right_type)}", dummy)
                return TypeKind.UNKNOWN
            return TypeKind.BOOLEAN

        # unknown operator
        dummy = type('',(object,),{'line':0,'column':0})()
        self.error(f"Unknown binary operator '{op}'", dummy)
        return TypeKind.UNKNOWN

    # debugging helper (tetap ada)
    def print_symbol_table(self):
        print("\n=== SYMBOL TABLE (TAB) ===")
        print(f"{'Idx':<5} {'ID':<15} {'Obj':<12} {'Type':<15} {'Ref':<5} {'Nrm':<5} {'Lev':<5} {'Adr':<5} {'Link':<5}")
        print("-" * 85)
        for i, entry in enumerate(self.symbol_tables.tab):
            link_0 = entry.link
            print(f"{i:<5} {entry.identifier:<15} {entry.obj:<12} {TypeKind.to_string(entry.type):<15} {entry.ref:<5} {entry.nrm:<5} {entry.lev:<5} {entry.adr:<5} {link_0:<5}")
