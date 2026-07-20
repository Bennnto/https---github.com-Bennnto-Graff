import ply.yacc as yacc
from lexicals import lexer, tokens
from typing import Optional, List
from dataclasses import dataclass

precedence = (
              ('left', 'EQ', 'NE'),
              ('left', 'LT', 'GT', 'LE', 'GE'),
              ('left', 'ADD', 'SUB'),
              ('left', 'DIV', 'MUL', 'MOD'),
              ('right', 'POW'),
              ('right', 'NOT',),
              ('right', 'LPAREN'),
              ('right', 'UMINUS'),
              )

class Node():
    pass

@dataclass
class Int_Node(Node):
    value : int
    
@dataclass
class Str_Node(Node):
    value : str

@dataclass    
class BinOps_Node(Node):
    left : str
    right : str
    ops : str

@dataclass    
class Type_Node(Node):
    type : str
    
@dataclass
class Assign_Node(Node):
    ident : str
    type : Optional[Type_Node]
    value : Node
    
@dataclass
class SingleOps_Node(Node):
    right : str
    ops : str
    
@dataclass 
class Variable_Node(Node):
    ident : str 
    
# Programs and Statements

def p_program(p):
    '''program : statements'''
    p[0] = p[1]
    
def p_statement(p):
    '''statement : expression optional_semicolon'''
    p[0] = p[1]
    
def p_statements(p):
    '''statements : statement
                  | statements statement'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]
        
def p_statement_empty(p):
    '''statement : empty'''
    p[0] = []
    
# Expression

def p_expression_variable(p):
    '''expression : variable'''
    p[0] = p[1]

def p_expression_binops(p):
    '''expression : bin_ops optional_semicolon'''
    p[0] = p[1]
    
# Variable

def p_variable(p):
    '''variable : INT
                | STR
                | ID'''
    if isinstance(p[1], int):
        p[0] = Int_Node(int(p[1]))
    elif isinstance(p[1], str):
        p[0] = Str_Node(str(p[1]))
    else :
        p[0] = Variable_Node(p[1])
        
# Single Operations

def p_single_ops_expr(p):
    '''expression : NOT expression
                  | SUB expression %prec UMINUS'''
    p[0] = SingleOps_Node(right= p[2], ops=p[1])
    
# Binary Operations

def p_binops_expr(p):
    '''bin_ops    : expression ADD expression
                  | expression SUB expression
                  | expression MUL expression
                  | expression DIV expression
                  | expression MOD expression
                  | expression POW expression
                  | expression GT expression
                  | expression LT expression
                  | expression GE expression
                  | expression LE expression
                  | expression EQ expression
                  | expression NE expression'''
    p[0] = BinOps_Node(left=p[1], right=p[3], ops=p[2])

# Type

def p_type(p):
    '''type : INT_TYPE
            | STR_TYPE'''
    p[0] = Type_Node(type=p[1])
    
# Assign

def p_assign_stmt(p):
    '''statement : LET ID COLON type ASSIGN expression optional_semicolon'''
    p[0] = Assign_Node(ident=p[2], type=p[4], value=p[6])
    
# Helper

def p_empty(p):
    '''empty : '''
    p[0] = []
    
def p_optional_semicolon(p):
    '''optional_semicolon : SEMICOLON
                          | empty'''
    pass

def p_error(p):
    if p:
        print(f"Syntax Error at token '{p.value}' line {p.lineno}, position {p.lexpos}")
    else:
        print("Unexpected end of input EOF")
        
parser = yacc.yacc()
if __name__ == "__main__":
    data = """let x:int = 5;
let y:int = 3;
y < x;
    """
    lexer.input(data)
    while True :
        tok = lexer.token()
        if not tok:
            break
        print(tok)
    result = parser.parse(data, lexer=lexer)
    print(result)