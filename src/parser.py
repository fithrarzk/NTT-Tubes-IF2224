from .token import Token

sym = Token('NONE', 'NONE', 0, 0)

class ParserError(Exception):
    pass

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0
    
    # FUNGSI YANG KITA BUTUHIN TAPI GADA DI SPEK DAH
    def next_token(self):
        if self.position < len(self.tokens):
            token = self.tokens[self.position]
            self.position += 1
            return token
        else:
            return Token('EOF', 'EOF', -1, -1)

    def accept(self, expected_type, expected_value):
        global sym
        if sym.type == expected_type and sym.value == expected_value:
            sym = self.next_token()
        else:
            raise ParserError(f'Expected {expected_value} of type {expected_type}, got {sym.value} of type {sym.type} at line {sym.line}, column {sym.column}')
        
    def accept_identifier(self):
        global sym
        if sym.type == 'IDENTIFIER':
            sym = self.next_token()
        else:
            raise ParserError(f'Expected IDENTIFIER, got {sym.value} at line {sym.line}, column {sym.column}')
    
    def parse(self):
        global sym
        # berarti mulai dari program
        sym = self.next_token()
        self.program_header()
        self.declaration_part()
        self.compound_statement()
        self.accept('DOT', '.')
    
    def block(self):
        global sym
        self.declaration_part()
        self.compound_statement()

    # JUJUR BINGUNG.    
    def type_definition(self):
        global sym
        if sym.type == 'KEYWORD' and sym.value == 'larik':
            self.accept('KEYWORD', 'larik')
            self.accept('LBRACKET', '[')
            self.range()
            self.accept('RBRACKET', ']')
            self.accept('KEYWORD', 'dari')
            self.type()
        else:
            self.type()
    
    # cek token berikutnya
    def peek_next_token(self):
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return None

    def statement(self):
        global sym

        if sym.type == 'IDENTIFIER':
            next_token = self.peek_next_token()
            if next_token and next_token.type == 'ASSIGN_OPERATOR':
                self.assignment_statement()
            else:
                self.procedure_call()
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

    # SEMUA FUNGSI SPEK TARO BAWAH INI
    def program_header(self):
        global sym
        self.accept('KEYWORD', 'program')
        self.accept_identifier()
        self.accept('SEMICOLON', ';')

# to-do: ubah biar bisa ganti-ganti urutannya
    def declaration_part(self):
        global sym
        while sym.type == 'KEYWORD' and sym.value == 'konstanta':
            self.constant_declaration()
        while sym.type == 'KEYWORD' and sym.value == 'tipe':
            self.type_declaration()
        while sym.type == 'KEYWORD' and sym.value == 'variabel':
            self.var_declaration()
        while sym.type == 'KEYWORD' and (sym.value == 'prosedur' or sym.value == 'fungsi'):
            self.subprogram_declaration()
    
    def constant_declaration(self):
        global sym
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
    
    def type_declaration(self):
        global sym
        self.accept('KEYWORD', 'tipe')
        self.accept_identifier()
        self.accept('RELATIONAL_OPEARTOR', '=')
        self.type_definition()
        self.accept('SEMICOLON', ';')

        while sym.type == 'IDENTIFIER':
            self.accept_identifier()
            self.accept('RELATIONAL_OPEARTOR', '=')
            self.type_definition()
            self.accept('SEMICOLON', ';')
    
    def var_declaration(self):
        global sym
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

    def identifier_list(self):
        global sym
        self.accept_identifier()
        while sym.type == 'COMMA' and sym.value == ',':
            self.accept('COMMA', ',')
            self.accept_identifier()
    
    def type(self):
        global sym
        if sym.type == 'KEYWORD' and sym.value in ('integer', 'real', 'boolean', 'char'):
            self.accept('KEYWORD', sym.value)
        elif sym.type == 'KEYWORD' and sym.value == 'larik':
            self.array_type()
        else:
            self.accept_identifier()
    
    def array_type(self):
        global sym
        self.accept('KEYWORD', 'larik')
        self.accept('LBRACKET', '[')
        self.range()
        self.accept('RBRACKET', ']')
        self.accept('KEYWORD', 'dari')
        self.type()
    
    def range(self):
        global sym
        self.expression()
        self.accept('RANGE_OPERATOR', '..')
        self.expression()

    def subprogram_declaration(self):
        global sym
        if sym.type == 'KEYWORD' and sym.value == 'prosedur':
            self.procedure_declaration()
        elif sym.type == 'KEYWORD' and sym.value == 'fungsi':
            self.function_declaration()

    def procedure_declaration(self):
        global sym
        self.accept('KEYWORD', 'prosedur')
        self.accept_identifier()
        if sym.type != 'SEMICOLON' and sym.value != ';':
            self.formal_parameter_list()
        self.accept('SEMICOLON', ';')
        self.block()
        self.accept('SEMICOLON', ';')

    def function_declaration(self):
        global sym
        self.accept('KEYWORD', 'fungsi')
        self.accept_identifier()
        if sym.type != 'COLON' and sym.value != ':':
            self.formal_parameter_list()
        self.accept('COLON', ':')
        self.type()
        self.accept('SEMICOLON', ';')
        self.block()
        self.accept('SEMICOLON', ';')

    def parameter_group(self):
        global sym
        self.identifier_list()
        self.accept('COLON', ':')
        self.type()

    def formal_parameter_list(self):
        global sym
        self.accept('LPARENTHESIS', '(')
        self.parameter_group()
        while sym.type == 'SEMICOLON' and sym.value == ';':
            self.accept('SEMICOLON',';')
            self.parameter_group()
        self.accept('RPARENTHESIS', ')')

    def compound_statement(self):
        global sym
        self.accept('KEYWORD', 'mulai')
        self.statement_list()
        self.accept('KEYWORD', 'selesai')

    def statement_list(self):
        global sym
        self.statement()
        while sym.type == 'SEMICOLON' and sym.value == ';':
            self.accept('SEMICOLON', ';')
            self.statement()

    def assignment_statement(self):
        global sym
        self.accept_identifier()
        self.accept('ASSIGN_OPERATOR', ':=')
        self.expression()

    def if_statement(self):
        global sym
        self.accept('KEYWORD', 'jika')
        self.expression()
        self.accept('KEYWORD', 'maka')
        self.statement()
        if sym.type == 'KEYWORD' and sym.value == 'selain_itu':
            self.accept('KEYWORD', 'selain_itu')
            self.statement()

    def while_statement(self):
        global sym
        self.accept('KEYWORD', 'selama')
        self.expression()
        self.accept('KEYWORD', 'lakukan')
        self.statement()

    def for_statement(self):
        global sym
        self.accept('KEYWORD', 'untuk')
        self.accept_identifier()
        self.accept('ASSIGN_OPERATOR', ':=')
        self.expression()
        if sym.type == 'KEYWORD' and sym.value in ('ke', 'turun_ke'):
            self.accept('KEYWORD', sym.value)
        self.expression()
        self.accept('KEYWORD', 'lakukan')
        self.statement()

    def procedure_call(self):
        global sym
        self.accept_identifier()
        if sym.type == 'LPARENTHESIS' and sym.value == '(':
            self.accept('LPARENTHESIS', '(')
            if sym.type != 'RPARENTHESIS' and sym.value != ')':
                self.parameter_list()
            self.accept('RPARENTHESIS', ')')

    def parameter_list(self):
        global sym
        self.expression()
        while sym.type == 'COMMA' and sym.value == ',':
            self.accept('COMMA', ',')
            self.expression()

    def expression(self):
        global sym
        self.simple_expression()
        if sym.type == 'RELATIONAL_OPERATOR':
            self.accept('RELATIONAL_OPERATOR', sym.value)
            self.simple_expression()

    def simple_expression(self):
        global sym
        if sym.type == 'ARITHMETIC_OPERATOR' and sym.value in ('+', '-'):
            self.accept('ARITHMETIC_OPERATOR', sym.value)
        self.term()
        while sym.type == 'ARITHMETIC_OPERATOR' and sym.value in ('+', '-'):
            self.additive_operator()
            self.term()

    def term(self):
        global sym
        self.factor()
        while (sym.type == 'ARITHMETIC_OPERATOR' and sym.value in ('*', '/')) or (sym.type == 'KEYWORD' and sym.value in ('bagi', 'mod', 'dan')):
            self.multiplicative_operator()
            self.factor() 


    def factor(self):
        global sym
        match sym.type:
            case 'IDENTIFIER':
                self.accept_identifier()
                if sym.type == 'LPARENTHESIS' and sym.value == '(':
                    self.function_params()
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

    def function_params(self):
        global sym
        self.accept('LPARENTHESIS', '(')
        if sym.type != 'RPARENTHESIS' and sym.value != ')':
            self.parameter_list()
        self.accept('RPARENTHESIS', ')')
    
    def relational_operator(self):
        global sym
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

    def additive_operator(self):
        global sym
        if sym.type == 'ARITHMETIC_OPERATOR':
            match sym.value:
                case '+':
                    self.accept('ARITHMETIC_OPERATOR', '+')
                case '-':
                    self.accept('ARITHMETIC_OPERATOR', '-')
        if sym.type == 'KEYWORD' and sym.value == 'atau':
            self.accept('KEYWORD','atau')

    def multiplicative_operator(self):
        global sym
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