class ASTNode:
    #Base class buat semua AST Nodes

    def __init__(self, line=None, column=None):
        self.type = None #disetnya pas type checking
        self.scope_level = None
        self.tab_index = None   # reference ke symbol table
        self.line = line  # line number dari source code
        self.column = column  # column number dari source code

    def __repr__(self):
        return f"{self.__class__.__name__}()"
    
class ProgramNode(ASTNode):
    #Node buat keseluruhan program
    def __init__(self, name, declarations, block, line=None, column=None):
        super().__init__(line, column)
        self.name = name
        self.declarations = declarations #list of declarations nodes
        self.block = block  # compound statement node

    def __repr__(self):
        return f"ProgramNode(name='{self.name}')"
    
class BlockNode(ASTNode):
    #Node buat block program (declarations + compound statement)
    def __init__(self, declarations, compound_statement, line=None, column=None):
        super().__init__(line, column)
        self.declarations = declarations  #list of declarations nodes
        self.compound_statement = compound_statement  #compound statement node

    def __repr__(self):
        return f"BlockNode()"
    
class CompoundStatementNode(ASTNode):
    #Node buat compound statement (BEGIN ... END)
    def __init__(self, statements, line=None, column=None):
        super().__init__(line, column)
        self.statements = statements  #list of statement nodes

    def __repr__(self):
        return f"CompoundStatementNode(statements={len(self.statements)})"
    
class VarDeclNode(ASTNode):
    #Node buat deklarasi variabel
    def __init__(self, names, type_name, line=None, column=None):
        super().__init__(line, column)
        self.names = names  #list of identifier strings
        self.type_name = type_name  #type string or typenode

    def __repr__(self):
        return f"VarDeclNode(names={self.names}, type='{self.type_name}')"
    
class ConstDeclNode(ASTNode):
    #Node buat deklarasi konstanta
    def __init__(self, name, value, line=None, column=None):
        super().__init__(line, column)
        self.name = name  #identifier string
        self.value = value  # NumberNode, StringNode, or UnaryOpNode

    def __repr__(self):
        return f"ConstDeclNode(name='{self.name}', value={self.value})"
    
class TypeDeclNode(ASTNode):
    #Node buat tipe data
    def __init__(self, name, type_name, line=None, column=None):
        super().__init__(line, column)
        self.name = name  #identifier string
        self.type_name = type_name  #TypeNode or ArrayTypeNode

    def __repr__(self):
        return f"TypeDeclNode(type_name='{self.type_name}')"
    
class ProcedureDeclNode(ASTNode):
    #Node buat deklarasi prosedur
    def __init__(self, name, params, block, line=None, column=None):
        super().__init__(line, column)
        self.name = name
        self.params = params #List of parameternode
        self.block = block  #blocknode

    def __repr__(self):
        return f"ProcedureDeclNode(name='{self.name}'), params={len(self.params)}"
    
class FunctionDeclNode(ASTNode):
    #Node buat deklarasi fungsi
    def __init__(self, name, params, return_type, block, line=None, column=None):
        super().__init__(line, column)
        self.name = name
        self.params = params #List of parameternode
        self.return_type = return_type
        self.block = block  #blocknode

    def __repr__(self):
        return f"FunctionDeclNode(name='{self.name}'), params={len(self.params)}, return_type='{self.return_type}'"
    
class ParameterNode(ASTNode):
    #Node buat parameter prosedur/fungsi
    def __init__(self, names, type_name, line=None, column=None):
        super().__init__(line, column)
        self.names = names  #list of identifier strings
        self.type_name = type_name  #type string

    def __repr__(self):
        return f"ParameterNode(names={self.names}, type='{self.type_name}')"
    
class TypeNode(ASTNode):
    #node buat tipe dasar (integer, real, dll)
    def __init__(self, name, type_name, line=None, column=None):
        super().__init__(line, column)
        self.type_name = type_name  #string
        self.type = type_name
    
    def __repr__(self):
        return f"TypeNode(name='{self.typename}')"
    
class ArrayTypeNode(ASTNode):
    #node buat tipe array
    def __init__(self, index_range, element_type, line=None, column=None):
        super().__init__(line, column)
        self.index_range = index_range  #RangeNode
        self.element_type = element_type  #TypeNode or ArrayTypeNode

    def __repr__(self):
        return f"ArrayTypeNode(index_range={self.index_range}, element_type='{self.element_type}')"
    
class RangeNode(ASTNode):
    #node buat range (low - high)
    def __init__(self, low, high, line=None, column=None):
        super().__init__(line, column)
        self.low = low  # Expression node
        self.high = high   # Expression node

    def __repr__(self):
        return f"RangeNode(low={self.low}, high={self.high})"
    
class AssignNode(ASTNode):
    #node buat assignment statement
    def __init__(self, target, value, line=None, column=None):
        super().__init__(line, column)
        self.target = target  # VarNode
        self.value = value  # Expression node

    def __repr__(self):
        return f"AssignNode(target = {self.target}, value = {self.value})"
    
class IfNode(ASTNode):
    #node buat if statement
    def __init__(self, condition, then_statement, else_statement=None, line=None, column=None):
        super().__init__(line, column)
        self.condition = condition  #expression node
        self.then_statement = then_statement    # statement node
        self.else_statement = else_statement    # statement node or None

    def __repr__(self):
        return f"IfNode(condition = {self.condition})"
    
class WhileNode(ASTNode):
    #node buat while statement
    def __init__(self, condition, body, line=None, column=None):
        super().__init__(line, column)
        self.condition = condition
        self.body = body    #statement node

    def __repr__(self):
        return f"WhileNode(condition = {self.condition})"
    
class ForNode(ASTNode):
    #node buat for statement
    def __init__(self, var, start_expr, end_expr, body, is_downto = False, line=None, column=None):
        super().__init__(line, column)
        self.var = var  #VarNode
        self.start_expr = start_expr  #expression node
        self.end_expr = end_expr  #expression node
        self.body = body  #statement node
        self.is_downto = is_downto  # True klo turun_ke, false kalo ke

    def __repr__(self):
        direction = "turun_ke" if self.is_downto else "ke"
        return f"ForNode(var={self.var}, {direction})"
    
class ProcedureFunctionCallNode(ASTNode):
    #Node buat procedure/function call
    def __init__(self, name, arguments, line=None, column=None):
        super().__init__(line, column)
        self.name = name #Procedure/function name (string)
        self.arguments = arguments #list of expression

    def __repr__(self):
        return f"ProcedureFunctionCallNode(name='{self.name}', arguments={len(self.arguments)})"
    
class BinOpNode(ASTNode):
    #node buat binary operation
    def __init__(self, left, op, right, line=None, column=None):
        super().__init__(line, column)
        self.left = left  #expression node 
        self.op = op      #operator string (+, -, *, /, =, <>, <, >, <=, >=, dan, atau, dll)
        self.right = right  #expression node

    def __repr__(self):
        return f"BinOpNode(op='{self.op}', left={self.left}, right={self.right})"

class UnaryOpNode(ASTNode):
    #node buat unary operation
    def __init__(self, op, operand, line=None, column=None):
        super().__init__(line, column)
        self.op = op  #operator string (+, -, not)
        self.operand = operand  #expression node

    def __repr__(self):
        return f"UnaryOpNode(op='{self.op}', operand={self.operand})"
    
class NumberNode(ASTNode):
    #node buat literal number
    def __init__(self, value, line=None, column=None):
        super().__init__(line, column)
        self.value = value  #numeric value
        from .symbol_table import TypeKind
        if isinstance(value, str):
            if '.' in value or 'e' in value.lower():
                self.type = TypeKind.REAL
            else:
                self.type = TypeKind.INTEGER
        elif isinstance(value, int):
            self.type = TypeKind.INTEGER
        else:
            self.type = TypeKind.REAL

    def __repr__(self):
        return f"NumberNode(value={self.value})"
    
class StringNode(ASTNode):
    #node buat literal string
    def __init__(self, value, line=None, column=None):
        super().__init__(line, column)
        self.value = value  #string value
        from .symbol_table import TypeKind
        self.type = TypeKind.STRING

    def __repr__(self):
        return f"StringNode(value='{self.value}')"
    
class CharNode(ASTNode):
    #node buat literal char
    def __init__(self, value, line=None, column=None):
        super().__init__(line, column)
        self.value = value  #char value
        from .symbol_table import TypeKind
        self.type = TypeKind.CHAR

    def __repr__(self):
        return f"CharNode(value='{self.value}')"
    
class VarNode(ASTNode):
    #node buat variabel
    def __init__(self, name, line=None, column=None):
        super().__init__(line, column)
        self.name = name  #variable name (string)

    def __repr__(self):
        return f"VarNode(name='{self.name}')"
    
class ArrayAccessNode(ASTNode):
    #node buat akses elemen array
    def __init__(self, array_var, index_expression, line=None, column=None):
        super().__init__(line, column)
        self.array_var = array_var  #VarNode
        self.index_expression = index_expression  #expression node
    
    def __repr__(self):
        return f"ArrayAccessNode(array_var={self.array_var}, index_expression={self.index_expression})"
    
class NoOpNode(ASTNode):
    #node buat no operation (kosong)
    def __init__(self, line=None, column=None):
        super().__init__(line, column)

    def __repr__(self):
        return "NoOpNode()"
    
def print_ast(node, indent=0, prefix=""):
    #print AST Tree dengan format yang rapi
    #param: node -> ast node buat diprint, indent -> level indent skrg, prefix -> buat struktur tree
    if node is None:
        return
    
    #print node skrg
    indent_str = " " * indent
    print(f"{indent_str}{prefix}{node}")

    #print child berdasarkan node type
    if isinstance(node, ProgramNode):
        print(f"{indent_str}  declarations:")
        for decl in node.declarations:
            print_ast(decl, indent + 2, "├── ")
        print(f"{indent_str}  Block:")
        print_ast(node.block, indent + 2, "└── ")
    
    elif isinstance(node, BlockNode):
        if node.declarations:
            print(f"{indent_str}  declarations:")
            for decl in node.declarations:
                print_ast(decl, indent + 2, "├── ")
        print(f"{indent_str}  Compound Statement:")
        print_ast(node.compound_statement, indent + 2, "└── ")
    
    elif isinstance(node, CompoundStatementNode):
        for i, stmt in enumerate(node.statements):
            is_last = (i == len(node.statements) - 1)
            prefix = "└── " if is_last else "├── "
            print_ast(stmt, indent + 1, prefix)
    
    elif isinstance(node, AssignNode):
        print(f"{indent_str}  Target:")
        print_ast(node.target, indent + 2, "├── ")
        print(f"{indent_str}  Value:")
        print_ast(node.value, indent + 2, "└── ")
    
    elif isinstance(node, BinOpNode):
        print(f"{indent_str}  Left:")
        print_ast(node.left, indent + 2, "├── ")
        print(f"{indent_str}  Right:")
        print_ast(node.right, indent + 2, "└── ")
    
    elif isinstance(node, UnaryOpNode):
        print(f"{indent_str}  Operand:")
        print_ast(node.operand, indent + 2, "└── ")
    
    elif isinstance(node, IfNode):
        print(f"{indent_str}  Condition:")
        print_ast(node.condition, indent + 2, "├── ")
        print(f"{indent_str}  Then:")
        print_ast(node.then_statement, indent + 2, "├── " if node.else_statement else "└── ")
        if node.else_statement:
            print(f"{indent_str}  Else:")
            print_ast(node.else_statement, indent + 2, "└── ")
    
    elif isinstance(node, WhileNode):
        print(f"{indent_str}  Condition:")
        print_ast(node.condition, indent + 2, "├── ")
        print(f"{indent_str}  Body:")
        print_ast(node.body, indent + 2, "└── ")
    
    elif isinstance(node, ForNode):
        print(f"{indent_str}  Start:")
        print_ast(node.start_expr, indent + 2, "├── ")
        print(f"{indent_str}  End:")
        print_ast(node.end_expr, indent + 2, "├── ")
        print(f"{indent_str}  Body:")
        print_ast(node.body, indent + 2, "└── ")
    
    elif isinstance(node, ProcedureFunctionCallNode):
        if node.arguments:
            print(f"{indent_str}  Arguments:")
            for i, arg in enumerate(node.arguments):
                is_last = (i == len(node.arguments) - 1)
                prefix = "└── " if is_last else "├── "
                print_ast(arg, indent + 2, prefix)
    
    elif isinstance(node, VarDeclNode):
        print(f"{indent_str}  Variables: {', '.join(node.names)}")
        print(f"{indent_str}  Type: {node.type_name}")
    
    elif isinstance(node, (ProcedureDeclNode, FunctionDeclNode)):
        if node.params:
            print(f"{indent_str}  Parameters:")
            for param in node.params:
                print_ast(param, indent + 2, "├── ")
        print(f"{indent_str}  Block:")
        print_ast(node.block, indent + 2, "└── ")

def ast_to_dict(node):
    # konversi AST ke dictionary buat serialisasi JSON
    #param: node -> ast node buat dikonversi
    #return: dictionary representasi AST
    if node is None:
        return None
    
    result = {
        'node_type': node.__class__.__name__,
        'type': node.type if hasattr(node, 'type') else None
    }
    
    if isinstance(node, ProgramNode):
        result['name'] = node.name
        result['declarations'] = [ast_to_dict(d) for d in node.declarations]
        result['block'] = ast_to_dict(node.block)
    
    elif isinstance(node, VarDeclNode):
        result['names'] = node.names
        result['type_name'] = node.type_name
    
    elif isinstance(node, AssignNode):
        result['target'] = ast_to_dict(node.target)
        result['value'] = ast_to_dict(node.value)
    
    elif isinstance(node, BinOpNode):
        result['op'] = node.op
        result['left'] = ast_to_dict(node.left)
        result['right'] = ast_to_dict(node.right)
    
    elif isinstance(node, (NumberNode, StringNode, CharNode)):
        result['value'] = node.value
    
    elif isinstance(node, VarNode):
        result['name'] = node.name
    
    elif isinstance(node, CompoundStatementNode):
        result['statements'] = [ast_to_dict(s) for s in node.statements]
    
    # tambahin node types yg dibutuhin lgi ntar klo ada
    
    return result