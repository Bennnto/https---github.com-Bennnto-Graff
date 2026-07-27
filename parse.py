import ply.yacc as yacc
from lexicals import lexer, tokens
from typing import Optional, List, Any
from dataclasses import dataclass

precedence = (
    ('left', 'EQ', 'NE'),
    ('left', 'LT', 'GT', 'LE', 'GE'),
    ('left', 'ADD', 'SUB'),
    ('left', 'DIV', 'MUL', 'MOD'),
    ('right', 'POW'),
    ('right', 'NOT'),
    ('right', 'LPAREN'),
    ('right', 'Uminus'),
)

class Node():
    pass

class Return_Exception(Exception):
    def __init__(self, value):
        self.value = value

class Break_Exception(Exception):
    pass

class Continue_Exception(Exception):
    pass

@dataclass
class Int_Node(Node):
    value : int
    
@dataclass
class Str_Node(Node):
    value : str

@dataclass
class Bool_Node(Node):
    value : bool
    
@dataclass 
class Float_Node(Node):
    value : float

@dataclass 
class Void_Node(Node):
    pass

@dataclass    
class BinOps_Node(Node):
    left : Node
    right : Node
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
    right : Node
    ops : str
    
@dataclass 
class Variable_Node(Node):
    ident : str 
    
@dataclass
class Disp_Node(Node):
    expr : Node
    
@dataclass
class Entry_Node(Node):
    expr : Optional[Node]
    

@dataclass
class While_Node(Node):
    condition : Node
    while_block : List[Node]
        
@dataclass 
class Continue_Node(Node):
    pass

@dataclass
class Break_Node(Node):
    pass

@dataclass
class Return_Node(Node):
    expr : Optional[Node]

@dataclass
class Param_Node(Node):
    ident : str
    type : Optional[Type_Node]
    value : Optional[Node]
    
@dataclass
class Function_Node(Node):
    ident : str
    re_type : Optional[Type_Node]
    parameter : Optional[List[Param_Node]]
    body : List[Node]

@dataclass
class Call_Node(Node):
    ident : str
    parameter : Optional[List[Node]]
    
@dataclass
class For_Node(Node):
    init : Optional[Node]
    condition : Node
    update : Optional[Node]
    for_block : List[Node]

@dataclass
class Array_Node(Node):
    elements : List[Node]

@dataclass
class Index_Node(Node):
    target : Node
    index : Node

@dataclass 
class Index_Assign_Node(Node):
    target : Node
    index : Node
    value : Node

@dataclass 
class Method_Call_Node(Node):
    target : Node
    method : str
    args : List[Node]

@dataclass
class Array_Type_Node(Node):
    elem_type : Node
    length : Optional[int] = None

@dataclass
class Hash_Node(Node):
    elements : List[tuple[Node, Node]]

@dataclass
class Hash_Type_Node(Node): 
    key_type : Node
    value_type : Node
    
@dataclass
class Throw_Node(Node):
    expr : Node

@dataclass
class Try_Ok_Node(Node):
    try_block : Any
    is_ok_ident : str
    err_ident : str
    ok_block : Any
    
@dataclass
class Assert_Node(Node):
    condition : Node
    message : Optional[Node] = None

@dataclass
class Assert_Eq_Node(Node):
    actual : Node
    expected : Node

@dataclass
class Attempt_Node(Node):
    retry : Node
    attempt_block : Node
    fallback_block : Node

@dataclass
class Lambda_Node(Node):
    params : list
    return_type : Any
    body : Node

@dataclass
class Box_Node(Node):
    expr : Node

@dataclass
class Move_Node(Node):
    var_name : str

@dataclass
class Ref_Node(Node):
    var_name : str
    is_mutable : bool

@dataclass
class Deref_Node(Node):
    expr : None

@dataclass
class Deref_Assign_Node(Node):
    target : Node
    value : Node

@dataclass
class Fstr_Node(Node):
    raw : str

@dataclass 
class Case_Node(Node):
    pattern : Node
    body : List[Node]

@dataclass 
class Match_Node(Node):
    target : Node
    cases : List[Case_Node]
    

# Programs and Statements

def p_program(p):
    '''program : statements'''
    p[0] = p[1]
    
def p_statement(p):
    '''statement : expression optional_semicolon
                 | assign_stmt
                 | statement_index_assign
                 | disp_stmt
                 | entry_stmt
                 | match_stmt
                 | while_stmt
                 | block
                 | function_stmt
                 | for_stmt
                 | continue_stmt
                 | break_stmt
                 | return_stmt
                 | call_stmt
                 | try_ok_stmt
                 | throw_stmt
                 | assert_stmt
                 | assert_eq_stmt
                 | attempt_stmt
                 | deref_assign_stmt'''
    p[0] = p[1]
    
def p_statements(p):
    '''statements : statement
                  | statements statement'''
    if len(p) == 2:
        p[0] = [p[1]] if p[1] is not None else []
    else:
        p[0] = p[1] + ([p[2]] if p[2] is not None else [])
        
def p_statement_empty(p):
    '''statement : empty'''
    p[0] = None
    
# User I/O statement display | entry

def p_disp_stmt(p):
    '''disp_stmt : DISP LPAREN expression RPAREN optional_semicolon'''
    p[0] = Disp_Node(expr=p[3])

def p_entry_stmt(p):
    '''entry_stmt : ENTRY LPAREN expression RPAREN optional_semicolon
                  | ENTRY optional_semicolon'''
    if len(p) == 3 :
        p[0] = Entry_Node(expr=None)
    else :
        p[0] = Entry_Node(expr=p[3])
    
# Expression

def p_expression_variable(p):
    '''expression : variable'''
    p[0] = p[1]

def p_expression_binops(p):
    '''expression : bin_ops'''
    p[0] = p[1]

def p_expression_paren(p):
    '''expression : LPAREN expression RPAREN'''
    p[0] = p[2]
    
# Variable

def p_variable(p):
    '''variable : INT
                | STR
                | BOOL
                | ID
                | FLOAT'''
    if isinstance(p[1], bool):
        p[0] = Bool_Node(p[1])
    elif isinstance(p[1], int):
        p[0] = Int_Node(int(p[1]))
    elif isinstance(p[1], str) and p.slice[1].type == 'STR':
        p[0] = Str_Node(str(p[1]))
    elif isinstance(p[1], float):
        p[0] = Float_Node(p[1])
    else :
        p[0] = Variable_Node(p[1])
        
# Block

def p_block(p):
    '''block : LBRACE statements RBRACE'''
    p[0] = p[2]

# While 

def p_while_stmt(p):
    '''while_stmt : WHILE expression block'''
    p[0] = While_Node(condition=p[2], while_block=p[3])

# For 

def p_for_stmt(p):
    '''for_stmt : FOR LPAREN statement expression SEMICOLON statement RPAREN block
                | FOR expression block'''
    if len(p) == 9:
        p[0] = For_Node(init=p[3], condition=p[4], update=p[6], for_block=p[8])
    else :
        p[0] = For_Node(init=None, condition=p[2], update=None, for_block=p[3])
        
# Continue & Break

def p_continue_stmt(p):
    '''continue_stmt : CONT optional_semicolon'''
    p[0] = Continue_Node()
    
def p_break_stmt(p):
    '''break_stmt : BREAK optional_semicolon'''
    p[0] = Break_Node()

# Return

def p_return_stmt(p):
    '''return_stmt : RETURN expression optional_semicolon
                   | RETURN optional_semicolon'''
    if len(p) == 4:
        p[0] = Return_Node(expr=p[2]) 
    else :
        p[0] = Return_Node(expr=None)
        
# Single Operations

def p_single_ops_expr(p):
    '''expression : NOT expression
                  | SUB expression %prec Uminus'''
    p[0] = SingleOps_Node(right=p[2], ops=p[1])

# Function and parameter

def p_param(p):
    '''param : ID COLON type ASSIGN expression
             | ID COLON type
             | ID ASSIGN expression
             | ID'''
    if len(p) == 4 and p[2] == ':':
        p[0] = Param_Node(ident=p[1], type=p[3], value=None)
    elif len(p) == 6 :
        p[0] = Param_Node(ident=p[1], type=p[3], value=p[5])
    elif len(p) == 4 and p[2] == '=':
        p[0] = Param_Node(ident=p[1], type=None, value=p[3])
    else :
        p[0] = Param_Node(ident=p[1], type=None, value=None)   

def p_params(p):
    '''params : param
              | params COMMA param'''
    if len(p) == 4 :
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]
        
def p_param_list(p):
    '''param_list : LBRACKET params RBRACKET
                  | LBRACKET empty RBRACKET'''
    p[0] = p[2]
    
def p_function_stmt(p):
    '''function_stmt : FUNCTION ID COLON type param_list COLON block
                     | FUNCTION ID param_list COLON block'''
    if len(p) == 8 :
        p[0] = Function_Node(ident=p[2], re_type=p[4], parameter=p[5], body=p[7])
    else :
        p[0] = Function_Node(ident=p[2], re_type=None, parameter=p[3], body=p[5])
        

def p_args(p):
    '''args : expression
            | args COMMA expression'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

def p_arg_list(p):
    '''arg_list : args
                | empty'''
    p[0] = p[1]

def p_call_stmt(p):
    '''call_stmt : ID LPAREN arg_list RPAREN'''
    p[0] = Call_Node(ident=p[1], parameter=p[3])

def p_expression_call(p):
    '''expression : call_stmt'''
    p[0] = p[1]

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
                  | expression NE expression
                  | expression AND expression
                  | expression OR expression'''
    p[0] = BinOps_Node(left=p[1], right=p[3], ops=p[2])

# Type

def p_type(p):
    '''type : INT_TYPE
            | STR_TYPE
            | BOOL_TYPE
            | FLOAT_TYPE
            | VOID_TYPE
            | type_array
            | type_hash'''
    if isinstance(p[1], Node):
        p[0] = p[1]
    else:
        p[0] = Type_Node(type=p[1])

def p_type_array(p):
    '''type_array : type ARRAY_TYPE LBRACKET INT RBRACKET
                  | type ARRAY_TYPE'''
    if len(p) == 6:
        p[0] = Array_Type_Node(elem_type=p[1], length=p[4])
    else:
        p[0] = Array_Type_Node(elem_type=p[1], length=None)
    
def p_type_hash(p):
    '''type_hash : HASH_TYPE LBRACKET type COMMA type RBRACKET
                 | HASH_TYPE'''
    if len(p) == 7 :
        p[0] = Hash_Type_Node(key_type=p[3], value_type=p[5])    
    else :
        p[0] = Hash_Type_Node(key_type=None, value_type=None)
        
# Assign

def p_assign_stmt(p):
    '''assign_stmt : LET ID COLON type ASSIGN expression optional_semicolon
                   | LET ID ASSIGN expression optional_semicolon
                   | ID ASSIGN expression optional_semicolon
                   | LET ID COLON type lambda_expr optional_semicolon'''
    if len(p) == 8:
        p[0] = Assign_Node(ident=p[2], type=p[4], value=p[6])
    elif len(p) == 7:
        p[0] = Assign_Node(ident=p[2], type=p[4], value=p[5])
    elif len(p) == 6:
        p[0] = Assign_Node(ident=p[2], type=None, value=p[4])
    else : 
        p[0] = Assign_Node(ident=p[1], type=None, value=p[3])

# List 

def p_expression_array(p):
    '''expression : LBRACKET args RBRACKET
                  | LBRACKET empty RBRACKET'''
    
    p[0] = Array_Node(elements=p[2])

def p_expression_index(p):
    '''expression : expression LBRACKET expression RBRACKET'''
    p[0] = Index_Node(target=p[1], index=p[3])

def p_statement_index_assign(p):
    '''statement_index_assign : expression LBRACKET expression RBRACKET ASSIGN expression optional_semicolon'''
    p[0] = Index_Assign_Node(target=p[1], index=p[3], value=p[6])

def p_expression_method_call(p):
    '''expression : expression DOT ID LPAREN arg_list RPAREN'''
    p[0] = Method_Call_Node(target=p[1], method=p[3], args=p[5])

# Hash

def p_expression_hash(p):
    '''expression : LBRACE hash_elements RBRACE
                  | LBRACE empty RBRACE'''
    p[0] = Hash_Node(elements=p[2])

def p_hash_element(p):
    '''hash_element : expression COLON expression'''
    p[0] = (p[1], p[3])

def p_hash_elements(p):
    '''hash_elements : hash_element
                     | hash_elements COMMA hash_element'''
    if len(p) == 2:
        p[0] = [p[1]]   
    else:
        p[0] = p[1] + [p[3]]

# Try and Throw

def p_throw_stmt(p):
    '''throw_stmt : THROW expression optional_semicolon'''
    p[0] = Throw_Node(expr=p[2])

def p_try_ok_stmt(p):
    '''try_ok_stmt : TRY COLON block OK_CHECK LBRACKET ID COMMA ID RBRACKET COLON block
                    | TRY COLON block OK_CHECK LBRACKET ID RBRACKET COLON block
                    | TRY COLON block OK_CHECK COLON block
                    | TRY COLON statements OK_CHECK LBRACKET ID COMMA ID RBRACKET COLON statements
                    | TRY COLON statements OK_CHECK LBRACKET ID RBRACKET COLON statements
                    | TRY COLON statements OK_CHECK COLON statements'''
    if len(p) == 12:
        p[0] = Try_Ok_Node(try_block=p[3], is_ok_ident=p[6], err_ident=p[8], ok_block=p[11])
    elif len(p) == 10:
        p[0] = Try_Ok_Node(try_block=p[3], is_ok_ident=p[6], err_ident="err", ok_block=p[9])
    else:
        p[0] = Try_Ok_Node(try_block=p[3], is_ok_ident="is_ok", err_ident="err", ok_block=p[6])

# Assert / Assert_Eq

def p_assert_stmt(p):
    '''assert_stmt : ASSERT expression COMMA expression optional_semicolon
                   | ASSERT expression optional_semicolon'''
    if len(p) == 6:
        p[0] = Assert_Node(condition=p[2], message=p[4])
    else:
        p[0] = Assert_Node(condition=p[2], message=None)

def p_assert_eq_stmt(p):
    '''assert_eq_stmt : ASSERT_EQ expression COMMA expression optional_semicolon'''
    p[0] = Assert_Eq_Node(actual=p[2], expected=p[4])
    
# Attempt / Fallback
def p_attempt_stmt(p):
    '''attempt_stmt : ATTEMPT LPAREN expression RPAREN COLON block FALLBACK COLON block
                    | ATTEMPT LPAREN expression RPAREN COLON block
                    | ATTEMPT LPAREN expression RPAREN COLON statements FALLBACK COLON statements
                    | ATTEMPT LPAREN expression RPAREN COLON statements'''
    if len(p) >= 9:
        p[0] = Attempt_Node(retry=p[3], attempt_block=p[6], fallback_block=p[9])
    elif len(p) == 7:
        p[0] = Attempt_Node(retry=p[3], attempt_block=p[6], fallback_block=None)

# Lambda as expression
def p_expression_from_lambda(p):
    '''expression : lambda_expr'''
    p[0] = p[1]

# Lambda Function 
def p_lambda_expr(p):
    '''lambda_expr : LAMBDA LPAREN params RPAREN COLON type THIN_ARROW expression
                   | LAMBDA LPAREN params RPAREN THIN_ARROW expression
                   | LAMBDA LPAREN RPAREN THIN_ARROW expression'''
    if len(p) == 9:
        p[0] = Lambda_Node(params=p[3], return_type=p[6], body=p[8])
    elif len(p) == 7:
        p[0] = Lambda_Node(params=p[3], return_type=None, body=p[6])
    else:
        p[0] = Lambda_Node(params=[], return_type=None, body=p[5])

# Memory
def p_expression_memory(p):
    '''expression : BOX LPAREN expression RPAREN
                  | MOVE ID
                  | LT ID GT
                  | MUL LT ID GT
                  | GT ID LT'''
    if p[1] == 'box':
        p[0] = Box_Node(expr=p[3])
    elif p[1] == 'move':
        p[0] = Move_Node(var_name=p[2])
    elif len(p) == 4 and p[1] == '<':
        p[0] = Ref_Node(var_name=p[2], is_mutable=False)
    elif len(p) == 5 and p[1] == '*':
        p[0] = Ref_Node(var_name=p[3], is_mutable=True)
    elif len(p) == 4 and p[1] == '>':
        p[0] = Deref_Node(expr=Variable_Node(ident=p[2]))

def p_statement_deref_assign(p):
    '''deref_assign_stmt : GT ID LT ASSIGN expression optional_semicolon'''
    p[0] = Deref_Assign_Node(target=Variable_Node(ident=p[2]), value=p[5])

# String Interpolation 

def p_expression_fstr(p):
    '''expression : FSTR'''
    p[0] = Fstr_Node(raw=p[1])

# Match Case

def p_case(p):
    '''case : CASE LPAREN expression RPAREN COLON block'''
    p[0] = Case_Node(pattern=p[3], body=p[6])

def p_cases(p):
    '''cases : case 
             | cases case'''
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 3:
        p[0] = p[1] + [p[2]]

def p_match_stmt(p):
    '''match_stmt : MATCH LPAREN expression RPAREN COLON cases'''
    p[0] = Match_Node(target=p[3], cases=p[6])


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