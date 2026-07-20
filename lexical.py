import ply.lex as lex

tokens = (
    # Type and Variable
    'INT',
    'INT_TYPE',
    
    # Operators
    'ADD',
    'SUB',
    'DIV',
    'MUL',
    
    # Delimeters
    'LPAREN',
    'RPAREN',
    'SEMICOLON',
    'COLON',
    
    # Keywords
    'ASSIGN',
    'ID',
    'LET'
)
reserved_keys = {
    'int' : 'INT_TYPE',
    'let' : 'LET',
    
}
t_ASSIGN = r'\='
t_ADD = r'\+'
t_SUB = r'\-'
t_DIV = r'\/'
t_MUL = r'\*'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_SEMICOLON = r'\;'
t_ignore = ' \t'
t_COLON = r'\:'

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