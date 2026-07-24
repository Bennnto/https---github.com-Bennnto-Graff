import ply.lex as lex

tokens = (
    # Type and Variable
    'INT',
    'INT_TYPE',
    'STR',
    'STR_TYPE',
    'BOOL',
    'BOOL_TYPE',
    'FLOAT',
    'FLOAT_TYPE',
    'VOID_TYPE',
    'ARRAY',
    
    # Arithmetic Operators
    'ADD',
    'SUB',
    'DIV',
    'MUL',
    'MOD',
    'POW',
    
    # Compare Operators
    'GT',
    'LT',
    'LE',
    'GE',
    'NE',
    'EQ',
    
    # Logical Operators
    'AND',
    'OR',
    
    # Unary and Not Operators
    'Uminus',
    'NOT',
    
    # Delimiters
    'LPAREN',
    'RPAREN',
    'LBRACE',
    'RBRACE',
    'SEMICOLON',
    'COLON',
    'LBRACKET',
    'RBRACKET',
    'COMMA',
    'DOT',
    
    # Keywords
    'ASSIGN',
    'ID',
    'LET',
    'DISP',
    'ENTRY',
    'IF',
    'ELSE',
    'WHILE',
    'BREAK',
    'CONT',
    'RETURN',
    'FUNCTION', 
    'FOR',
)

reserved_keys = {
    'int' : 'INT_TYPE',
    'str' : 'STR_TYPE',
    'bool' : 'BOOL_TYPE',
    'let' : 'LET',
    'disp' : 'DISP',
    'entry': 'ENTRY',
    'if' : 'IF',
    'else' : 'ELSE',
    'while': 'WHILE',
    'break' : 'BREAK',
    'cont' : 'CONT',
    'return' : 'RETURN',
    'fn': 'FUNCTION',
    'void': 'VOID_TYPE',
    'float': 'FLOAT_TYPE',
    'for' : 'FOR',
    'array': 'ARRAY',
}

t_ASSIGN = r'\='
t_POW = r'\*\*'
t_ADD = r'\+'
t_SUB = r'-'
t_DIV = r'/'
t_MUL = r'\*'
t_MOD = r'%'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_SEMICOLON = r';'
t_ignore = ' \t'
t_COLON = r':'
t_LE = r'<='
t_GE = r'>='
t_NE = r'!='
t_EQ = r'=='   
t_GT = r'>'
t_LT = r'<'
t_NOT = r'!'
t_OR = r'\|'
t_AND = r'&'
t_COMMA = r','
t_DOT = r'\.'

def t_ID(t):
    r'[A-Za-z_][A-Za-z0-9_]*'
    t.type = reserved_keys.get(t.value, "ID")
    return t

def t_STR(t):
    r'\"[^"\n]*\"|\'[^\'\n]*\''
    t.value = t.value[1:-1]
    return t

def t_FLOAT(t):
    r'-?[0-9]+\.[0-9]+'
    t.value = float(t.value)
    return t

def t_INT(t):
    r'-?[0-9]+'
    t.value = int(t.value)
    return t

def t_BOOL(t):
    r'true|false'
    t.value = t.value == 'true'
    return t

def t_NEWLINE(t):
    r'\n'
    t.lexer.lineno += len(t.value)
    
def t_error(t):
    print(f"Illegal Character {t.value[0]}")
    t.lexer.skip(1)
    
lexer = lex.lex()
if __name__ == "__main__":
    data = "x = 2"
    lexer.input(data)
    while True:
        tok = lexer.token()
        if not tok:
            break
        print(tok)