import ply.lex as lex

tokens = (
    # Type and Variable
    'INT',
    'INT_TYPE',
    'STR',
    'STR_TYPE',
    
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
    
    # Unary and Not Operators
    'Uminus',
    'NOT',
    
    # Delimeters
    'LPAREN',
    'RPAREN',
    'SEMICOLON',
    'COLON',
    
    # Keywords
    'ASSIGN',
    'ID',
    'LET',
)
reserved_keys = {
    'int' : 'INT_TYPE',
    'str' : 'STR_TYPE',
    'let' : 'LET',
    
}
t_ASSIGN = r'\='
t_ADD = r'\+'
t_SUB = r'-'
t_DIV = r'/'
t_MUL = r'\*'
t_POW = r'\*\*'
t_MOD = r'%'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_SEMICOLON = r';'
t_ignore = ' \t'
t_COLON = r':'
t_GT = r'>'
t_LT = r'<'
t_LE = r'<='
t_GE = r'>='
t_NE = r'!='
t_EQ = r'=='   
t_NOT = r'!'


def t_STR(t):
    r'\"[^"\n]*\"|\'[^\'\n]*\''
    t.value = t.value[1:-1]
    return t

def t_INT(t):
    r'-?[0-9]+'
    t.value = int(t.value)
    return t
    
def t_ID(t):
    r'[A-Za-z_][A-Za-z0-9_]*'
    t.type = reserved_keys.get(t.value, "ID")
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