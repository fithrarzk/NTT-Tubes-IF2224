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
            return Token('EOF', 'EOF')

    def accept(self, expected_type, expected_value):
        global sym
        if sym.type == expected_type and sym.value == expected_value:
            sym = self.next_token()
        else:
            raise ParserError(f'Expected {expected_value}, got {sym.value} at line {sym.line}, column {sym.column}')
        
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
        self.accept('DOT')
    
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

    # SEMUA FUNGSI SPEK TARO BAWAH INI
    def program_header(self):
        global sym
        self.accept('KEYWORD', 'program')
        self.accept_identifier()
        self.accept('SEMICOLON', ';')

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
        self.accept('EQUALS', '=')
        match sym.type:
            case 'NUMBER':
                self.accept('NUMBER', sym.value)
            case 'ARITHMETIC_OP' if sym.value in ('+', '-'):
                self.accept('ARITHMETIC_OP', sym.value)
                self.accept('NUMBER', sym.value)
            case 'STRING_LITERAL':
                self.accept('STRING_LITERAL', sym.value)
        self.accept('SEMICOLON', ';')

        while sym.type == 'IDENTIFIER':
            self.accept_identifier()
            self.accept('EQUALS', '=')
            match sym.type:
                case 'NUMBER':
                    self.accept('NUMBER', sym.value)
                case 'ARITHMETIC_OP' if sym.value in ('+', '-'):
                    self.accept('ARITHMETIC_OP', sym.value)
                    self.accept('NUMBER', sym.value)
                case 'STRING_LITERAL':
                    self.accept('STRING_LITERAL', sym.value)
            self.accept('SEMICOLON', ';')
    
    def type_declaration(self):
        global sym
        self.accept('KEYWORD', 'tipe')
        self.accept_identifier()
        self.accept('EQUALS', '=')
        self.type_definition()
        self.accept('SEMICOLON', ';')

        while sym.type == 'IDENTIFIER':
            self.accept_identifier()
            self.accept('EQUALS', '=')
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
        self.accept('DOUBLE_DOT', '..')
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
    
