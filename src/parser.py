from .token import Token
from .ast_nodes import *

sym = Token('NONE', 'NONE', 0, 0)
i = 0

class ParserError(Exception):
    pass

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0
        self.tree_list = []
    
    # FUNGSI YANG KITA BUTUHIN TAPI GADA DI SPEK DAH
    def next_token(self):
        if self.position < len(self.tokens):
            token = self.tokens[self.position]
            self.position += 1
            return token
        else:
            return Token('EOF', 'EOF', -1, -1)

    def accept(self, expected_type, expected_value):
        global sym, i
        i += 1
        if sym.type == expected_type and sym.value == expected_value:
            self.tree_list.append((str(sym), i))
            current = sym
            sym = self.next_token()
            i -= 1
            return current
        else:
            raise ParserError(f'Expected {expected_value} of type {expected_type}, got {sym.value} of type {sym.type} at line {sym.line}, column {sym.column}')
        
    def accept_identifier(self):
        global sym, i
        i += 1
        if sym.type == 'IDENTIFIER':
            self.tree_list.append((str(sym), i))
            current = sym
            sym = self.next_token()
            i -= 1
            return current
        else:
            raise ParserError(f'Expected IDENTIFIER, got {sym.value} at line {sym.line}, column {sym.column}')
        

    def parse(self):
        global sym
        sym = self.next_token()
        ast = self.program()
        return ast
    
    def program(self):
        global sym, i
        self.tree_list.append(("<program>", i)) 
        name = self.program_header()
        declarations = self.declaration_part()
        block = self.compound_statement()
        self.accept('DOT', '.')
        return ProgramNode(name=name, declarations=declarations, block=block)

        
    def block(self):
        global sym,i
        i += 1
        self.tree_list.append(("<block>", i))
        declarations = self.declaration_part()
        compound_stmt = self.compound_statement()
        i -= 1
        return BlockNode(declarations=declarations, compound_statement=compound_stmt)

    def type_definition(self):
        global sym,i
        i += 1
        self.tree_list.append(("<type_definition>", i))
        result = None
        if sym.type == 'KEYWORD' and sym.value == 'larik':
            result = self.array_type()
        else:
            result = self.type()
        i -= 1
        return result
    
    def peek_next_token(self):
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return None

    # SEMUA FUNGSI SPEK TARO BAWAH INI
    def program_header(self):
        global sym,i
        i += 1
        self.tree_list.append(("<program_header>", i))
        self.accept('KEYWORD', 'program')
        name_token = self.accept_identifier()
        self.accept('SEMICOLON', ';')
        i -= 1
        return name_token.value

    def declaration_part(self):
        global sym,i
        i += 1
        self.tree_list.append(("<declaration_part>", i))

        declarations = []

        while sym.type == 'KEYWORD' and sym.value in ('konstanta', 'tipe', 'variabel'):
            if sym.value == 'konstanta':
                declarations.extend(self.constant_declaration())
            elif sym.value == 'tipe':
                declarations.extend(self.type_declaration())
            elif sym.value == 'variabel':
                declarations.extend(self.var_declaration())
        while sym.type == 'KEYWORD' and (sym.value == 'prosedur' or sym.value == 'fungsi'):
            declarations.append(self.subprogram_declaration())
        
        i -= 1
        return declarations
    
    def constant_declaration(self):
        global sym, i
        i += 1
        self.tree_list.append(("<constant_declaration>", i))

        const_nodes = []

        self.accept('KEYWORD', 'konstanta')
        name_token = self.accept_identifier()
        self.accept('RELATIONAL_OPERATOR', '=')

        value_node = None
        match sym.type:
            case 'NUMBER':
                num_token = self.accept('NUMBER', sym.value)
                value_node = NumberNode(value=num_token.value)
            case 'ARITHMETIC_OPERATOR' if sym.value in ('+', '-'):
                op_token = self.accept('ARITHMETIC_OPERATOR', sym.value)
                num_token = self.accept('NUMBER', sym.value)
                value_node = UnaryOpNode(op=op_token.value, operand=NumberNode(value=num_token.value))
            case 'STRING_LITERAL':
                str_token = self.accept('STRING_LITERAL', sym.value)
                value_node = StringNode(value=str_token.value)

        self.accept('SEMICOLON', ';')
        const_nodes.append(ConstDeclNode(name=name_token.value, value=value_node))

        while sym.type == 'IDENTIFIER':
            name_token = self.accept_identifier()
            self.accept('RELATIONAL_OPERATOR', '=')

            value_node = None
            match sym.type:
                case 'NUMBER':
                    num_token = self.accept('NUMBER', sym.value)
                    value_node = NumberNode(value=num_token.value)
                case 'ARITHMETIC_OPERATOR' if sym.value in ('+', '-'):
                    op_token = self.accept('ARITHMETIC_OPERATOR', sym.value)
                    num_token = self.accept('NUMBER', sym.value)
                    value_node = UnaryOpNode(op=op_token.value, operand=NumberNode(value=num_token.value))
                case 'STRING_LITERAL':
                    str_token = self.accept('STRING_LITERAL', sym.value)
                    value_node = StringNode(value=str_token.value)

            self.accept('SEMICOLON', ';')
            const_nodes.append(ConstDeclNode(name=name_token.value, value=value_node))
        
        i -= 1
        return const_nodes

    def type_declaration(self):
        global sym,i
        i += 1
        self.tree_list.append(("<type_declaration>", i))

        type_nodes = []

        self.accept('KEYWORD', 'tipe')
        name_token = self.accept_identifier()
        self.accept('RELATIONAL_OPERATOR', '=')
        type_def = self.type_definition()
        self.accept('SEMICOLON', ';')

        type_nodes.append(TypeDeclNode(name=name_token.value, type_name=type_def))

        while sym.type == 'IDENTIFIER':
            name_token = self.accept_identifier()
            self.accept('RELATIONAL_OPERATOR', '=')
            type_def = self.type_definition()
            self.accept('SEMICOLON', ';')
            type_nodes.append(TypeDeclNode(name=name_token.value, type_name=type_def))
        
        i -= 1
        return type_nodes
    
    def var_declaration(self):
        global sym,i
        i += 1
        self.tree_list.append(("<var_declaration>", i))

        var_nodes = []

        self.accept('KEYWORD', 'variabel')
        names = self.identifier_list()
        self.accept('COLON', ':')
        type_name = self.type()
        self.accept('SEMICOLON', ';')

        var_nodes.append(VarDeclNode(names=names, type_name = type_name))

        while sym.type == 'IDENTIFIER':
            names = self.identifier_list()
            self.accept('COLON', ':')
            type_name = self.type()
            self.accept('SEMICOLON', ';')
            var_nodes.append(VarDeclNode(names=names, type_name = type_name))
        
        i -= 1
        return var_nodes

    def identifier_list(self):
        global sym,i
        i += 1
        self.tree_list.append(("<identifier_list>", i))

        names = []
        name_token = self.accept_identifier()
        names.append(name_token.value)

        while sym.type == 'COMMA' and sym.value == ',':
            self.accept('COMMA', ',')
            name_token = self.accept_identifier()
            names.append(name_token.value)
        
        i -= 1
        return names
    
    def type(self):
        global sym,i
        i += 1
        self.tree_list.append(("<type>", i))

        type_name = None
        if sym.type == 'KEYWORD' and sym.value in ('integer', 'real', 'boolean', 'char'):
            type_token = self.accept('KEYWORD', sym.value)
            type_name = type_token.value
        elif sym.type == 'KEYWORD' and sym.value == 'larik':
            type_name = self.array_type()
        else:
            id_token = self.accept_identifier()
            type_name = id_token.value
        
        i -= 1
        return type_name
    
    def array_type(self):
        global sym,i
        i += 1
        self.tree_list.append(("<array_type>", i))

        self.accept('KEYWORD', 'larik')
        self.accept('LBRACKET', '[')
        range_node = self.range()
        self.accept('RBRACKET', ']')
        self.accept('KEYWORD', 'dari')
        element_type = self.type()
        
        i -= 1
        return ArrayTypeNode(index_range=range_node, element_type=element_type)
    
    def range(self):
        global sym,i
        i += 1
        self.tree_list.append(("<range>", i))

        low_expr = self.expression()
        self.accept('RANGE_OPERATOR', '..')
        high_expr = self.expression()
        
        i -= 1
        return RangeNode(low=low_expr, high=high_expr)

    def subprogram_declaration(self):
        global sym,i
        i += 1
        self.tree_list.append(("<subprogram_declaration>", i))

        result = None
        if sym.type == 'KEYWORD' and sym.value == 'prosedur':
            result = self.procedure_declaration()
        elif sym.type == 'KEYWORD' and sym.value == 'fungsi':
            result = self.function_declaration()
        
        i -= 1
        return result

    def procedure_declaration(self):
        global sym,i
        i += 1
        self.tree_list.append(("<procedure_declaration>", i))

        self.accept('KEYWORD', 'prosedur')
        name_token = self.accept_identifier()

        params = []

        if sym.type != 'SEMICOLON' and sym.value != ';':
            params = self.formal_parameter_list()
        self.accept('SEMICOLON', ';')
        block = self.block()
        self.accept('SEMICOLON', ';')
        
        i -= 1
        return ProcedureDeclNode(name=name_token.value, params=params, block=block)

    def function_declaration(self):
        global sym,i
        i += 1
        self.tree_list.append(("<function_declaration>", i))

        self.accept('KEYWORD', 'fungsi')
        name_token = self.accept_identifier()

        params = []

        if sym.type != 'COLON' and sym.value != ':':
            params = self.formal_parameter_list()
        
        self.accept('COLON', ':')
        return_type = self.type()
        self.accept('SEMICOLON', ';')
        block = self.block()
        self.accept('SEMICOLON', ';')
        
        i -= 1
        return FunctionDeclNode(name=name_token.value, params=params, return_type=return_type, block=block)

    def parameter_group(self):
        global sym,i
        i += 1
        self.tree_list.append(("<parameter_group>", i))

        names = self.identifier_list()
        self.accept('COLON', ':')
        type_name = self.type()
        
        i -= 1
        return ParameterNode(names=names, type_name=type_name)

    def formal_parameter_list(self):
        global sym,i
        i += 1
        self.tree_list.append(("<formal_parameter_list>", i))

        params = []
        self.accept('LPARENTHESIS', '(')
        params.append(self.parameter_group())

        while sym.type == 'SEMICOLON' and sym.value == ';':
            self.accept('SEMICOLON',';')
            params.append(self.parameter_group())
        self.accept('RPARENTHESIS', ')')
        
        i -= 1
        return params

    def compound_statement(self):
        global sym,i
        i += 1
        self.tree_list.append(("<compound_statement>", i))
        
        self.accept('KEYWORD', 'mulai')
        statements = self.statement_list()
        self.accept('KEYWORD', 'selesai')
        
        i -= 1
        return CompoundStatementNode(statements=statements)

    def statement_list(self):
        global sym,i
        i += 1
        self.tree_list.append(("<statement_list>", i))

        statements = []

        if sym.type == 'IDENTIFIER':
            next_token = self.peek_next_token()
            if next_token and next_token.type == 'ASSIGN_OPERATOR':
                stmt = self.assignment_statement()
                statements.append(stmt)
            else:
                stmt = self.procedure_function_call()
                statements.append(stmt)
        else:
            if sym.value == 'mulai':
                stmt = self.compound_statement()
                statements.append(stmt)
            elif sym.value == 'jika':
                stmt = self.if_statement()
                statements.append(stmt)
            elif sym.value == 'selama':
                stmt = self.while_statement()
                statements.append(stmt)
            elif sym.value == 'untuk':
                stmt = self.for_statement()
                statements.append(stmt)
            else:
                pass

        while sym.type == 'SEMICOLON' and sym.value == ';':
            self.accept('SEMICOLON', ';')

            if sym.value == 'selesai':
                break

            if sym.type == 'IDENTIFIER':
                next_token = self.peek_next_token()
                if next_token and next_token.type == 'ASSIGN_OPERATOR':
                    stmt = self.assignment_statement()
                    statements.append(stmt)
                else:
                    stmt = self.procedure_function_call()
                    statements.append(stmt)
            else:
                if sym.value == 'mulai':
                    stmt = self.compound_statement()
                    statements.append(stmt)
                elif sym.value == 'jika':
                    stmt = self.if_statement()
                    statements.append(stmt)
                elif sym.value == 'selama':
                    stmt = self.while_statement()
                    statements.append(stmt)
                elif sym.value == 'untuk':
                    stmt = self.for_statement()
                    statements.append(stmt)
                else:
                    pass
        i -= 1
        return statements

    def assignment_statement(self):
        global sym,i
        i += 1
        self.tree_list.append(("<assignment_statement>", i))

        target_token = self.accept_identifier()
        
        if sym.type == 'LBRACKET':
            self.accept('LBRACKET', '[')
            index_expr = self.expression()
            self.accept('RBRACKET', ']')
            target = ArrayAccessNode(array_name=target_token.value, index=index_expr)
        else:
            target = VarNode(name=target_token.value)

        self.accept('ASSIGN_OPERATOR', ':=')
        value_expr = self.expression()
        
        i -= 1
        return AssignNode(target=target, value=value_expr)
    
    def if_statement(self):
        global sym,i
        i += 1
        self.tree_list.append(("<if_statement>", i))

        self.accept('KEYWORD', 'jika')
        condition = self.expression()
        self.accept('KEYWORD', 'maka')

        then_stmt = None
        if sym.type == 'IDENTIFIER':
            next_token = self.peek_next_token()
            if next_token and next_token.type == 'ASSIGN_OPERATOR':
                then_stmt = self.assignment_statement()
            else:
                then_stmt = self.procedure_function_call()
        else:
            if sym.value == 'mulai':
                then_stmt = self.compound_statement()
            elif sym.value == 'jika':
                then_stmt = self.if_statement()
            elif sym.value == 'selama':
                then_stmt = self.while_statement()
            elif sym.value == 'untuk':
                then_stmt = self.for_statement()
            else:
                pass

        else_stmt = None
        if sym.type == 'KEYWORD' and sym.value == 'selain_itu':
            self.accept('KEYWORD', 'selain_itu')
            if sym.type == 'IDENTIFIER':
                next_token = self.peek_next_token()
                if next_token and next_token.type == 'ASSIGN_OPERATOR':
                    else_stmt = self.assignment_statement()
                else:
                    else_stmt = self.procedure_function_call()
            else:
                if sym.value == 'mulai':
                    else_stmt = self.compound_statement()
                elif sym.value == 'jika':
                    else_stmt = self.if_statement()
                elif sym.value == 'selama':
                    else_stmt = self.while_statement()
                elif sym.value == 'untuk':
                    else_stmt = self.for_statement()
                else:
                    pass
        
        i -= 1
        return IfNode(condition=condition, then_statement=then_stmt, else_statement=else_stmt)

    def while_statement(self):
        global sym,i
        i += 1
        self.tree_list.append(("<while_statement>", i))

        self.accept('KEYWORD', 'selama')
        condition = self.expression()
        self.accept('KEYWORD', 'lakukan')

        body = None
        if sym.type == 'IDENTIFIER':
            next_token = self.peek_next_token()
            if next_token and next_token.type == 'ASSIGN_OPERATOR':
                body = self.assignment_statement()
            else:
                body = self.procedure_function_call()
        else:
            if sym.value == 'mulai':
                body = self.compound_statement()
            elif sym.value == 'jika':
                body = self.if_statement()
            elif sym.value == 'selama':
                body = self.while_statement()
            elif sym.value == 'untuk':
                body = self.for_statement()
            else:
                pass
        
        i -= 1
        return WhileNode(condition=condition, body=body)

    def for_statement(self):
        global sym,i
        i += 1
        self.tree_list.append(("<for_statement>", i))

        self.accept('KEYWORD', 'untuk')
        var_token = self.accept_identifier()
        self.accept('ASSIGN_OPERATOR', ':=')
        start_expr = self.expression()

        is_downto = False
        if sym.type == 'KEYWORD' and sym.value in ('ke', 'turun_ke'):
            direction = self.accept('KEYWORD', sym.value)
            is_downto = (direction.value == 'turun_ke')

        end_expr = self.expression()
        self.accept('KEYWORD', 'lakukan')

        body = None
        if sym.type == 'IDENTIFIER':
            next_token = self.peek_next_token()
            if next_token and next_token.type == 'ASSIGN_OPERATOR':
                body = self.assignment_statement()
            else:
                body = self.procedure_function_call()
        else:
            if sym.value == 'mulai':
                body = self.compound_statement()
            elif sym.value == 'jika':
                body = self.if_statement()
            elif sym.value == 'selama':
                body = self.while_statement()
            elif sym.value == 'untuk':
                body = self.for_statement()
            else:
                pass
        
        i -= 1
        return ForNode(var=VarNode(name=var_token.value), start_expr=start_expr, end_expr=end_expr, body=body, is_downto=is_downto)

    def procedure_function_call(self):
        global sym,i
        i += 1
        self.tree_list.append(("<procedure_function_call>", i))

        name_token = self.accept_identifier()
        self.accept('LPARENTHESIS', '(')
        arguments = self.parameter_list()
        self.accept('RPARENTHESIS', ')')
        
        i -= 1
        return ProcedureFunctionCallNode(name=name_token.value, arguments=arguments)
        
    def parameter_list(self):
        global sym,i
        i += 1
        self.tree_list.append(("<parameter_list>", i))

        params = []

        if sym.type != 'RPARENTHESIS':
            params.append(self.expression())
            
            while sym.type == 'COMMA' and sym.value == ',':
                self.accept('COMMA', ',')
                params.append(self.expression())
        
        i -= 1
        return params

    def expression(self):
        global sym,i
        i += 1
        self.tree_list.append(("<expression>", i))
        left = self.simple_expression()

        if sym.type == 'RELATIONAL_OPERATOR':
            op_token = self.accept('RELATIONAL_OPERATOR', sym.value)
            right = self.simple_expression()
            i -= 1
            return BinOpNode(left=left, op=op_token.value, right=right)
        
        i -= 1
        return left

    def simple_expression(self):
        global sym,i
        i += 1
        self.tree_list.append(("<simple_expression>", i))
        if sym.type == 'ARITHMETIC_OPERATOR' and sym.value in ('+', '-'):
            self.accept('ARITHMETIC_OPERATOR', sym.value)
        self.term()
        while sym.type == 'ARITHMETIC_OPERATOR' and sym.value in ('+', '-'):
            self.additive_operator()
            self.term()
        i -= 1

    def term(self):
        global sym,i
        i += 1
        self.tree_list.append(("<term>", i))
        left = self.factor()
        while ((sym.type == 'ARITHMETIC_OPERATOR' and sym.value in ('*', '/')) or (sym.type == 'KEYWORD' and sym.value in ('bagi', 'mod', 'dan'))):
            if sym.type == 'ARITHMETIC_OPERATOR':
                op_token = self.accept('ARITHMETIC_OPERATOR', sym.value)
            else:
                op_token = self.accept('KEYWORD', sym.value)
            
            right = self.factor()
            left = BinOpNode(left=left, op=op_token.value, right=right)
        
        i -= 1
        return left


    def factor(self):
        global sym, i
        i += 1
        self.tree_list.append(("<factor>", i))
        
        result = None
        
        match sym.type:
            case 'IDENTIFIER':
                next_token = self.peek_next_token()
                if next_token and next_token.type == 'LPARENTHESIS':
                    result = self.procedure_function_call()
                elif next_token and next_token.type == 'LBRACKET':
                    id_token = self.accept_identifier()
                    self.accept('LBRACKET', '[')
                    index_expr = self.expression()
                    self.accept('RBRACKET', ']')
                    result = ArrayAccessNode(array_name=id_token.value, index=index_expr)
                else:
                    id_token = self.accept_identifier()
                    result = VarNode(name=id_token.value)
            
            case 'NUMBER': 
                num_token = self.accept('NUMBER', sym.value)
                result = NumberNode(value=num_token.value)
            
            case 'CHAR_LITERAL':
                char_token = self.accept('CHAR_LITERAL', sym.value)
                result = CharNode(value=char_token.value)
            
            case 'STRING_LITERAL': 
                str_token = self.accept('STRING_LITERAL', sym.value)
                result = StringNode(value=str_token.value)
            
            case 'LPARENTHESIS':
                self.accept('LPARENTHESIS', '(')
                result = self.expression()
                self.accept('RPARENTHESIS', ')')
            
            case 'KEYWORD': 
                if sym.value == 'tidak':
                    self.accept('KEYWORD', 'tidak')
                    operand = self.factor()
                    result = UnaryOpNode(op='tidak', operand=operand)
        
        i -= 1
        return result
    
    def relational_operator(self):
        global sym,i
        i += 1
        self.tree_list.append(("<relational_operator>", i))
        if sym.type == 'RELATIONAL_OPERATOR':
            match sym.value:
                case '=':
                    self.accept('RELATIONAL_OPERATOR', '=')
                case '<>':
                    self.accept('RELATIONAL_OPERATOR', '<>')
                case '<':
                    self.accept('RELATIONAL_OPERATOR', '<')
                case '<=':
                    self.accept('RELATIONAL_OPERATOR', '<=')
                case '>':
                    self.accept('RELATIONAL_OPERATOR', '>')
                case '>=':
                    self.accept('RELATIONAL_OPERATOR', '>=')
        i -= 1

    def additive_operator(self):
        global sym,i
        i += 1
        self.tree_list.append(("<additive_operator>", i))
        if sym.type == 'ARITHMETIC_OPERATOR':
            match sym.value:
                case '+':
                    self.accept('ARITHMETIC_OPERATOR', '+')
                case '-':
                    self.accept('ARITHMETIC_OPERATOR', '-')
        if sym.type == 'KEYWORD' and sym.value == 'atau':
            self.accept('KEYWORD','atau')
        i -= 1

    def multiplicative_operator(self):
        global sym,i
        i += 1
        self.tree_list.append(("<multiplicative_operator>", i))
        if sym.type == 'ARITHMETIC_OPERATOR':
            match sym.value:
                case '*':
                    self.accept('ARITHMETIC_OPERATOR', '*')
                case '/':
                    self.accept('ARITHMETIC_OPERATOR', '/')
        if sym.type == 'KEYWORD':
            match sym.value:
                case 'bagi':
                    self.accept('KEYWORD', 'bagi')
                case 'mod':
                    self.accept('KEYWORD', 'mod')
                case 'dan':
                    self.accept('KEYWORD', 'dan')
        i -= 1