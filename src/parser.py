from .token import Token

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
            sym = self.next_token()
        else:
            raise ParserError(f'Expected {expected_value} of type {expected_type}, got {sym.value} of type {sym.type} at line {sym.line}, column {sym.column}')
        i -= 1
        
    def accept_identifier(self):
        global sym, i
        i += 1
        if sym.type == 'IDENTIFIER':
            self.tree_list.append((str(sym), i))
            sym = self.next_token()
        else:
            raise ParserError(f'Expected IDENTIFIER, got {sym.value} at line {sym.line}, column {sym.column}')
        i -= 1

    def parse(self):
        global sym
        sym = self.next_token()
        self.program()
        return self.tree_list
    
    def program(self):
        global sym, i
        self.tree_list.append(("<program>", i))
        self.program_header()
        self.declaration_part()
        self.compound_statement()
        self.accept('DOT', '.')
        
    def block(self):
        global sym,i
        i += 1
        self.tree_list.append(("<block>", i))
        self.declaration_part()
        self.compound_statement()
        i -= 1

    def type_definition(self):
        global sym,i
        i += 1
        self.tree_list.append(("<type_definition>", i))
        if sym.type == 'KEYWORD' and sym.value == 'larik':
            self.accept('KEYWORD', 'larik')
            self.accept('LBRACKET', '[')
            self.range()
            self.accept('RBRACKET', ']')
            self.accept('KEYWORD', 'dari')
            self.type()
        else:
            self.type()
        i -= 1
    
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
        self.accept_identifier()
        self.accept('SEMICOLON', ';')
        i -= 1

    def declaration_part(self):
        global sym,i
        i += 1
        self.tree_list.append(("<declaration_part>", i))
        while sym.type == 'KEYWORD' and sym.value in ('konstanta', 'tipe', 'variabel'):
            if sym.value == 'konstanta':
                self.constant_declaration()
            elif sym.value == 'tipe':
                self.type_declaration()
            elif sym.value == 'variabel':
                self.var_declaration()
        while sym.type == 'KEYWORD' and (sym.value == 'prosedur' or sym.value == 'fungsi'):
            self.subprogram_declaration()
        i -= 1
    
    def constant_declaration(self):
        global sym,i
        i += 1
        self.tree_list.append(("<constant_declaration>", i))
        self.accept('KEYWORD', 'konstanta')
        self.accept_identifier()
        self.accept('RELATIONAL_OPERATOR', '=')
        match sym.type:
            case 'NUMBER':
                self.accept('NUMBER', sym.value)
            case 'ARITHMETIC_OPERATOR' if sym.value in ('+', '-'):
                self.accept('ARITHMETIC_OPERATOR', sym.value)
                self.accept('NUMBER', sym.value)
            case 'STRING_LITERAL':
                self.accept('STRING_LITERAL', sym.value)
        self.accept('SEMICOLON', ';')

        while sym.type == 'IDENTIFIER':
            self.accept_identifier()
            self.accept('RELATIONAL_OPERATOR', '=')
            match sym.type:
                case 'NUMBER':
                    self.accept('NUMBER', sym.value)
                case 'ARITHMETIC_OPERATOR' if sym.value in ('+', '-'):
                    self.accept('ARITHMETIC_OPERATOR', sym.value)
                    self.accept('NUMBER', sym.value)
                case 'STRING_LITERAL':
                    self.accept('STRING_LITERAL', sym.value)
            self.accept('SEMICOLON', ';')
        i -= 1
    
    def type_declaration(self):
        global sym,i
        i += 1
        self.tree_list.append(("<type_declaration>", i))
        self.accept('KEYWORD', 'tipe')
        self.accept_identifier()
        self.accept('RELATIONAL_OPERATOR', '=')
        self.type_definition()
        self.accept('SEMICOLON', ';')

        while sym.type == 'IDENTIFIER':
            self.accept_identifier()
            self.accept('RELATIONAL_OPERATOR', '=')
            self.type_definition()
            self.accept('SEMICOLON', ';')
        i -= 1
    
    def var_declaration(self):
        global sym,i
        i += 1
        self.tree_list.append(("<var_declaration>", i))
        self.accept('KEYWORD', 'variabel')
        self.identifier_list()
        self.accept('COLON', ':')
        self.type()
        self.accept('SEMICOLON', ';')

        while sym.type == 'IDENTIFIER':
            self.identifier_list()
            self.accept('COLON', ':')
            self.type()
            self.accept('SEMICOLON', ';')
        i -= 1

    def identifier_list(self):
        global sym,i
        i += 1
        self.tree_list.append(("<identifier_list>", i))
        self.accept_identifier()
        while sym.type == 'COMMA' and sym.value == ',':
            self.accept('COMMA', ',')
            self.accept_identifier()
        i -= 1
    
    def type(self):
        global sym,i
        i += 1
        self.tree_list.append(("<type>", i))
        if sym.type == 'KEYWORD' and sym.value in ('integer', 'real', 'boolean', 'char'):
            self.accept('KEYWORD', sym.value)
        elif sym.type == 'KEYWORD' and sym.value == 'larik':
            self.array_type()
        else:
            self.accept_identifier()
        i -= 1
    
    def array_type(self):
        global sym,i
        i += 1
        self.tree_list.append(("<array_type>", i))
        self.accept('KEYWORD', 'larik')
        self.accept('LBRACKET', '[')
        self.range()
        self.accept('RBRACKET', ']')
        self.accept('KEYWORD', 'dari')
        self.type()
        i -= 1
    
    def range(self):
        global sym,i
        i += 1
        self.tree_list.append(("<range>", i))
        self.expression()
        self.accept('RANGE_OPERATOR', '..')
        self.expression()
        i -= 1

    def subprogram_declaration(self):
        global sym,i
        i += 1
        self.tree_list.append(("<subprogram_declaration>", i))
        if sym.type == 'KEYWORD' and sym.value == 'prosedur':
            self.procedure_declaration()
        elif sym.type == 'KEYWORD' and sym.value == 'fungsi':
            self.function_declaration()
        i -= 1

    def procedure_declaration(self):
        global sym,i
        i += 1
        self.tree_list.append(("<procedure_declaration>", i))
        self.accept('KEYWORD', 'prosedur')
        self.accept_identifier()
        if sym.type != 'SEMICOLON' and sym.value != ';':
            self.formal_parameter_list()
        self.accept('SEMICOLON', ';')
        self.block()
        self.accept('SEMICOLON', ';')
        i -= 1

    def function_declaration(self):
        global sym,i
        i += 1
        self.tree_list.append(("<function_declaration>", i))
        self.accept('KEYWORD', 'fungsi')
        self.accept_identifier()
        if sym.type != 'COLON' and sym.value != ':':
            self.formal_parameter_list()
        self.accept('COLON', ':')
        self.type()
        self.accept('SEMICOLON', ';')
        self.block()
        self.accept('SEMICOLON', ';')
        i -= 1

    def parameter_group(self):
        global sym,i
        i += 1
        self.tree_list.append(("<parameter_group>", i))
        self.identifier_list()
        self.accept('COLON', ':')
        self.type()
        i -= 1

    def formal_parameter_list(self):
        global sym,i
        i += 1
        self.tree_list.append(("<formal_parameter_list>", i))
        self.accept('LPARENTHESIS', '(')
        self.parameter_group()
        while sym.type == 'SEMICOLON' and sym.value == ';':
            self.accept('SEMICOLON',';')
            self.parameter_group()
        self.accept('RPARENTHESIS', ')')
        i -= 1

    def compound_statement(self):
        global sym,i
        i += 1
        self.tree_list.append(("<compound_statement>", i))
        self.accept('KEYWORD', 'mulai')
        self.statement_list()
        self.accept('KEYWORD', 'selesai')
        i -= 1

    def statement_list(self):
        global sym,i
        i += 1
        self.tree_list.append(("<statement_list>", i))
        if sym.type == 'IDENTIFIER':
            next_token = self.peek_next_token()
            if next_token and next_token.type == 'ASSIGN_OPERATOR':
                self.assignment_statement()
            else:
                self.procedure_function_call()
        else:
            if sym.value == 'mulai':
                self.compound_statement()
            elif sym.value == 'jika':
                self.if_statement()
            elif sym.value == 'selama':
                self.while_statement()
            elif sym.value == 'untuk':
                self.for_statement()
            else:
                pass
        while sym.type == 'SEMICOLON' and sym.value == ';':
            self.accept('SEMICOLON', ';')
            if sym.type == 'IDENTIFIER':
                next_token = self.peek_next_token()
                if next_token and next_token.type == 'ASSIGN_OPERATOR':
                    self.assignment_statement()
                else:
                    self.procedure_function_call()
            else:
                if sym.value == 'mulai':
                    self.compound_statement()
                elif sym.value == 'jika':
                    self.if_statement()
                elif sym.value == 'selama':
                    self.while_statement()
                elif sym.value == 'untuk':
                    self.for_statement()
                else:
                    pass
        i -= 1

    def assignment_statement(self):
        global sym,i
        i += 1
        self.tree_list.append(("<assignment_statement>", i))
        self.accept_identifier()
        self.accept('ASSIGN_OPERATOR', ':=')
        self.expression()
        i -= 1

    def if_statement(self):
        global sym,i
        i += 1
        self.tree_list.append(("<if_statement>", i))
        self.accept('KEYWORD', 'jika')
        self.expression()
        self.accept('KEYWORD', 'maka')
        if sym.type == 'IDENTIFIER':
            next_token = self.peek_next_token()
            if next_token and next_token.type == 'ASSIGN_OPERATOR':
                self.assignment_statement()
            else:
                self.procedure_function_call()
        else:
            if sym.value == 'mulai':
                self.compound_statement()
            elif sym.value == 'jika':
                self.if_statement()
            elif sym.value == 'selama':
                self.while_statement()
            elif sym.value == 'untuk':
                self.for_statement()
            else:
                pass
        if sym.type == 'KEYWORD' and sym.value == 'selain_itu':
            self.accept('KEYWORD', 'selain_itu')
            if sym.type == 'IDENTIFIER':
                next_token = self.peek_next_token()
                if next_token and next_token.type == 'ASSIGN_OPERATOR':
                    self.assignment_statement()
                else:
                    self.procedure_function_call()
            else:
                if sym.value == 'mulai':
                    self.compound_statement()
                elif sym.value == 'jika':
                    self.if_statement()
                elif sym.value == 'selama':
                    self.while_statement()
                elif sym.value == 'untuk':
                    self.for_statement()
                else:
                    pass
        i -= 1

    def while_statement(self):
        global sym,i
        i += 1
        self.tree_list.append(("<while_statement>", i))
        self.accept('KEYWORD', 'selama')
        self.expression()
        self.accept('KEYWORD', 'lakukan')
        if sym.type == 'IDENTIFIER':
            next_token = self.peek_next_token()
            if next_token and next_token.type == 'ASSIGN_OPERATOR':
                self.assignment_statement()
            else:
                self.procedure_function_call()
        else:
            if sym.value == 'mulai':
                self.compound_statement()
            elif sym.value == 'jika':
                self.if_statement()
            elif sym.value == 'selama':
                self.while_statement()
            elif sym.value == 'untuk':
                self.for_statement()
            else:
                pass
        i -= 1

    def for_statement(self):
        global sym,i
        i += 1
        self.tree_list.append(("<for_statement>", i))
        self.accept('KEYWORD', 'untuk')
        self.accept_identifier()
        self.accept('ASSIGN_OPERATOR', ':=')
        self.expression()
        if sym.type == 'KEYWORD' and sym.value in ('ke', 'turun_ke'):
            self.accept('KEYWORD', sym.value)
        self.expression()
        self.accept('KEYWORD', 'lakukan')
        if sym.type == 'IDENTIFIER':
            next_token = self.peek_next_token()
            if next_token and next_token.type == 'ASSIGN_OPERATOR':
                self.assignment_statement()
            else:
                self.procedure_function_call()
        else:
            if sym.value == 'mulai':
                self.compound_statement()
            elif sym.value == 'jika':
                self.if_statement()
            elif sym.value == 'selama':
                self.while_statement()
            elif sym.value == 'untuk':
                self.for_statement()
            else:
                pass
        i -= 1

    def procedure_function_call(self):
        global sym,i
        i += 1
        self.tree_list.append(("<procedure_function_call>", i))
        self.accept_identifier()
        self.accept('LPARENTHESIS', '(')
        self.parameter_list()
        self.accept('RPARENTHESIS', ')')
        i -= 1
        
    def parameter_list(self):
        global sym,i
        i += 1
        self.tree_list.append(("<parameter_list>", i))
        self.expression()
        while sym.type == 'COMMA' and sym.value == ',':
            self.accept('COMMA', ',')
            self.expression()
        i -= 1

    def expression(self):
        global sym,i
        i += 1
        self.tree_list.append(("<expression>", i))
        self.simple_expression()
        if sym.type == 'RELATIONAL_OPERATOR':
            self.accept('RELATIONAL_OPERATOR', sym.value)
            self.simple_expression()
        i -= 1

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
        self.factor()
        while (sym.type == 'ARITHMETIC_OPERATOR' and sym.value in ('*', '/')) or (sym.type == 'KEYWORD' and sym.value in ('bagi', 'mod', 'dan')):
            self.multiplicative_operator()
            self.factor()
        i -= 1


    def factor(self):
        global sym,i
        i += 1
        self.tree_list.append(("<factor>", i))
        match sym.type:
            case 'IDENTIFIER':
                next_token = self.peek_next_token()
                if next_token and next_token.type == 'LPARENTHESIS':
                    self.procedure_function_call()
                else:
                    self.accept_identifier()
            case 'NUMBER': 
                self.accept('NUMBER',sym.value)
            case 'CHAR_LITERAL':
                self.accept('CHAR_LITERAL',sym.value)
            case 'STRING_LITERAL': 
                self.accept('STRING_LITERAL',sym.value)
            case 'LPARENTHESIS':
                self.accept('LPARENTHESIS', '(')
                self.expression()
                self.accept('RPARENTHESIS',')')
            case 'KEYWORD': 
                if sym.value == 'tidak':
                    self.accept('KEYWORD','tidak')
                    self.factor()
        i -= 1
    
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