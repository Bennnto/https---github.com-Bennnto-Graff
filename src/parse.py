import re
import ply.yacc as yacc
from lexicals import lexer, tokens
from typing import Optional, List, Any
from dataclasses import dataclass, field

precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', 'EQ', 'NE'),
    ('left', 'LT', 'GT', 'LE', 'GE'),
    ('left', 'ADD', 'SUB'),
    ('left', 'DIV', 'MUL', 'MOD'),
    ('right', 'POW'),
    ('right', 'NOT'),
    ('right', 'LPAREN'),
    ('right', 'Uminus'),
    ('left', 'DOT', 'LBRACKET'),
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
    index : Optional[Node] = None

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
    expr : Node

@dataclass
class Deref_Assign_Node(Node):
    target : Node
    value : Node

@dataclass
class Fstr_Node(Node):
    raw : str = ""
    parts : List[Any] = field(default_factory=list)

@dataclass
class Case_Node(Node):
    pattern : Node
    body : List[Node]

@dataclass
class Match_Node(Node):
    target : Node
    cases : List[Case_Node]

@dataclass
class Ternary_Node(Node):
    condition : Node
    true_block : Node
    false_block : Node

@dataclass
class Timeline_Decl(Node):
    ident : str
    type : Node
    value : Node

@dataclass
class Timeline_Index_Node(Node):
    index : Node
    target : Node

@dataclass
class Timeline_Rollback_Node(Node):
    ident : str
    type : Optional[Node] = None
    index : Optional[Node] = None

@dataclass
class Enum_Node(Node):
    name : str
    members : List[Node]

@dataclass
class Bind_Node(Node):
    path : Node
    alias : Optional[Node] = None

@dataclass
class Pub_Node(Node):
    node : object

@dataclass
class Range_Node(Node):
    amount : Optional[Node] = None
    start : Optional[Node] = None
    stop : Optional[Node] = None
    step: Optional[Node] = None
@dataclass 
class For_Range_Node(Node):
    ident : str
    range: Node
    for_block : List[Node]

@dataclass
class Fix_Node(Node):
    ident : str
    type: Type_Node
    value : Node

@dataclass
class Generic_Type_Node(Node):
    name : str
    type_args : list

@dataclass
class Struct_Decl_Node(Node):
    name : str
    fields : dict
    type_params : list = None

@dataclass
class Struct_Literal_Node(Node):
    name : str
    field_values : dict
    type_args : list = None

@dataclass 
class Field_Access_Node(Node):
    target : Node
    field : str

@dataclass
class Impl_Node(Node):
    struct_name : str
    methods : list

@dataclass
class Drop_Node(Node):
    target : str

@dataclass
class Async_Node(Node):
    func : Function_Node

@dataclass
class Await_Node(Node):
    expr : Node

@dataclass
class Gaff_Node(Node):
    ident : str
    gaff_block : List[Node]

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
                 | deref_assign_stmt
                 | timeline_stmt
                 | rollback_stmt
                 | bind_stmt
                 | pub_stmt
                 | async_stmt
                 | gaff_stmt'''
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
    '''while_stmt : WHILE expression block
                | WHILE LPAREN expression RPAREN block'''
    if len(p) == 4:
        p[0] = While_Node(condition=p[2], while_block=p[3])
    else:
        p[0] = While_Node(condition=p[3], while_block=p[5])

# For

def p_for_stmt(p):
    '''for_stmt : FOR LPAREN statement expression SEMICOLON statement RPAREN block
                | FOR ID IN range block
                | FOR ID range block
                | FOR expression block'''
    if len(p) == 9:
        p[0] = For_Node(init=p[3], condition=p[4], update=p[6], for_block=p[8])
    elif len(p) == 6:
        p[0] = For_Range_Node(ident=p[2], range=p[4], for_block=p[5])
    elif len(p) == 5:
        p[0] = For_Range_Node(ident=p[2], range=p[3], for_block=p[4])
    else: 
        p[0] = For_Node(init=None, condition=p[2], update=None, for_block=p[3])
        
def p_range_expr(p):
    '''range_expr : expression DDOT expression COMMA expression
                  | expression DDOT expression
                  | expression DDOT
                  | DDOT expression'''
    if len(p) == 6:
        p[0] = Range_Node(amount=None, start=p[1], stop=p[3], step=p[5])
    elif len(p) == 4:
        p[0] = Range_Node(amount=None, start=p[1], stop=p[3], step=None)
    elif len(p) == 3 and p[2] == '..':
        p[0] = Range_Node(amount=None, start=p[1], stop=None, step=None)
    else:
        p[0] = Range_Node(amount=None, start=None, stop=p[2], step=None)

def p_range_node(p):
    '''range : expression DDOT expression COMMA expression
             | expression DDOT expression
             | expression DDOT
             | expression'''
    if len(p) == 6 :
        p[0] = Range_Node(amount=None, start=p[1], stop=p[3], step=p[5])
    elif len(p) == 4 :
        p[0] = Range_Node(amount=None, start=p[1], stop=p[3], step=None)
    elif len(p) == 3 :
        p[0] = Range_Node(amount=None, start=p[1], stop=None, step=None)
    else : 
        p[0] = Range_Node(amount=p[1], start=None, stop=None, step = None)

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
                  | BITNOT expression
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
    '''function_stmt : FUNCTION ID COLON type param_list block
                     | FUNCTION ID param_list block'''
    if len(p) == 7:
        p[0] = Function_Node(ident=p[2], re_type=p[4], parameter=p[5], body=p[6])
    else:
        p[0] = Function_Node(ident=p[2], re_type=None, parameter=p[3], body=p[4])


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
    '''expression : expression ADD expression
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
                  | expression OR expression
                  | expression LSHIFT expression
                  | expression RSHIFT expression
                  | expression XOR expression'''
    p[0] = BinOps_Node(left=p[1], right=p[3], ops=p[2])

# Type

def p_type(p):
    '''type : INT_TYPE
            | STR_TYPE
            | BOOL_TYPE
            | FLOAT_TYPE
            | VOID_TYPE
            | ID
            | type_generic
            | type_array
            | type_hash'''
    if isinstance(p[1], Node):
        p[0] = p[1]
    else:
        p[0] = Type_Node(type=p[1])

def p_type_generic(p):
    '''type_generic : ID LT type_args_list GT'''
    p[0] = Generic_Type_Node(name=p[1], type_args=p[3])

def p_type_args_list_single(p):
    '''type_args_list : type'''
    p[0] = [p[1]]

def p_type_args_list_multi(p):
    '''type_args_list : type_args_list COMMA type'''
    p[0] = p[1] + [p[3]]

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
    '''expression : expression LBRACKET range_expr RBRACKET
                  | expression LBRACKET expression RBRACKET'''
    p[0] = Index_Node(target=p[1], index=p[3])


def p_statement_index_assign(p):
    '''statement_index_assign : expression LBRACKET expression RBRACKET ASSIGN expression optional_semicolon'''
    p[0] = Index_Assign_Node(target=p[1], index=p[3], value=p[6])

def p_expression_dot(p):
    '''expression : expression DOT ID'''
    p[0] = Field_Access_Node(target=p[1], field=p[3])

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
    '''try_ok_stmt  : TRY COLON block OK_CHECK LBRACKET ID COMMA ID RBRACKET COLON block
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
                  | LT ID GT %prec Uminus
                  | MUL LT ID GT %prec Uminus
                  | GT ID LT %prec Uminus'''
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

_fstr_sub_parser = None

def get_fstr_sub_parser():
    global _fstr_sub_parser
    if _fstr_sub_parser is None:
        _fstr_sub_parser = yacc.yacc(tabmodule='parsetab', write_tables=False)
    return _fstr_sub_parser

def parse_fstr_parts(raw: str) -> List[Any]:
    parts = []
    last_end = 0
    sub_parser = get_fstr_sub_parser()
    for match in re.finditer(r'\{([^}]+)\}', raw):
        prefix = raw[last_end:match.start()]
        if prefix:
            parts.append(prefix)
        expr_text = match.group(1).strip()
        if expr_text:
            sub_lexer = lexer.clone()
            expr_ast = sub_parser.parse(expr_text, lexer=sub_lexer)
            if isinstance(expr_ast, list) and len(expr_ast) > 0:
                parts.append(expr_ast[0])
            elif expr_ast is not None:
                parts.append(expr_ast)
        last_end = match.end()
    suffix = raw[last_end:]
    if suffix:
        parts.append(suffix)
    return parts

def p_expression_fstr(p):
    '''expression : FSTR'''
    p[0] = Fstr_Node(raw=p[1], parts=parse_fstr_parts(p[1]))

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

# Ternary Operator

def p_expression_ternary(p):
    '''expression : expression TERNARY expression COLON expression'''
    p[0] = Ternary_Node(condition=p[1], true_block=p[3], false_block=p[5])

# HISTORY

def p_timeline_stmt(p):
    '''timeline_stmt : LET TIMELINE ID COLON type ASSIGN expression optional_semicolon
                     | LET TIMELINE ID ASSIGN expression optional_semicolon'''
    if len(p) == 9:
        p[0] = Timeline_Decl(ident=p[3], type=p[5], value=p[7])
    else:
        p[0] = Timeline_Decl(ident=p[3], type=None, value=p[5])

def p_expression_timeline_index(p):
    '''expression : expression AT expression'''
    p[0] = Timeline_Index_Node(index=p[3], target=p[1])

def p_timeline_rollback(p):
    '''rollback_stmt : ROLLBACK ID AT expression optional_semicolon'''
    p[0] = Timeline_Rollback_Node(ident=p[2], index=p[4])

# Enum

def p_enum_stmt(p):
    '''statement : ENUM ID COLON enum_body optional_semicolon'''
    p[0] = Enum_Node(name=p[2], members=p[4])

def p_enum_body(p):
    '''enum_body : enum_member_list
                 | enum_member_list COMMA'''
    p[0] = p[1]

def p_enum_member_list(p):
    '''enum_member_list : enum_member
                        | enum_member_list enum_member'''
    if len(p) == 3 :
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]

def p_enum_member(p):
    '''enum_member : ID
                   | ID ASSIGN expression'''
    if len(p) == 2 :
        p[0] = (p[1], None)
    else:
        p[0] = (p[1], p[3])

# Bind and Pub module
def p_module_ident(p):
    '''module_ident : ID
                    | ARRAY
                    | ARRAY_TYPE
                    | STR_TYPE
                    | INT_TYPE
                    | FLOAT_TYPE
                    | BOOL_TYPE
                    | HASH_TYPE'''
    p[0] = str(p[1])

def p_module_path(p):
    '''module_path : STR
                   | module_ident DCOLON module_ident
                   | module_ident DOT module_ident
                   | module_ident
                   | DOT DIV module_ident DOT module_ident
                   | DOT DOT DIV module_ident DOT module_ident
                   | module_ident DIV module_ident DOT module_ident'''
    if p.slice[1].type == 'STR':
        p[0] = Str_Node(p[1])
    else:
        full_str = "".join(str(p[i]) for i in range(1, len(p)))
        p[0] = Str_Node(full_str)

def p_symbol_list(p):
    '''symbol_list : ID
                   | symbol_list COMMA ID'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_bind_stmt(p):
    '''bind_stmt : BIND module_path DCOLON ID optional_semicolon
                 | BIND module_path DCOLON expression optional_semicolon
                 | BIND module_path DCOLON MUL optional_semicolon
                 | BIND module_path DCOLON LBRACE symbol_list RBRACE optional_semicolon'''
    if p[4] == '*':
        alias_node = "*"
    elif len(p) >= 7 and p[4] == '{':
        alias_node = p[5]
    else:
        alias_node = p[4]
    p[0] = Bind_Node(path=p[2], alias=alias_node)

def p_pub_stmt(p):
    '''pub_stmt : PUBLIC function_stmt'''
    p[0] = Pub_Node(node=p[2])

# Fix
def p_expression_fix(p):
    '''expression : FIX ID COLON type ASSIGN expression'''
    p[0] = Fix_Node(ident=p[2], type=p[4], value=p[6])

# Struct and fields

def p_statement_struct_decl(p):
    '''statement : STRUCT ID LBRACE struct_fields RBRACE
                 | STRUCT ID LT type_params_list GT LBRACE struct_fields RBRACE'''
    if len(p) == 6:
        p[0] = Struct_Decl_Node(name=p[2], fields=p[4])
    else:
        p[0] = Struct_Decl_Node(name=p[2], type_params=p[4], fields=p[7])

def p_type_params_list_single(p):
    '''type_params_list : ID'''
    p[0] = [p[1]]

def p_type_params_list_multi(p):
    '''type_params_list : type_params_list COMMA ID'''
    p[0] = p[1] + [p[3]]

def p_struct_fields_single(p):
    '''struct_fields : ID COLON type'''
    p[0] = {p[1]: p[3]}

def p_struct_fields_multi(p):
    '''struct_fields : struct_fields COMMA ID COLON type'''
    p[0] = dict(p[1])
    p[0][p[3]] = p[5]

def p_struct_literal(p):
    '''expression : ID LBRACE struct_init_list RBRACE
                  | ID DCOLON LT type_args_list GT LBRACE struct_init_list RBRACE'''
    if len(p) == 5:
        p[0] = Struct_Literal_Node(name=p[1], field_values=p[3])
    else:
        p[0] = Struct_Literal_Node(name=p[1], type_args=p[4], field_values=p[7])

def p_struct_init_list_single(p):
    '''struct_init_list : ID COLON expression'''
    p[0] = {p[1]: p[3]}

def p_struct_init_list_multi(p):
    '''struct_init_list : struct_init_list COMMA ID COLON expression'''
    p[0] = dict(p[1])
    p[0][p[3]] = p[5]

# Impl Block
def p_statement_impl(p):
    '''statement : IMPL ID LBRACE function_list RBRACE'''
    p[0] = Impl_Node(struct_name=p[2], methods=p[4])

def p_function_list_single(p):
    '''function_list : function_stmt'''
    p[0] = [p[1]]

def p_function_list_multi(p):
    '''function_list : function_list function_stmt'''
    p[0] = p[1] + [p[2]]

# Drop
def p_drop_expression(p):
    '''expression : DROP ID optional_semicolon'''
    p[0] = Drop_Node(target=p[2])


# Async & Await
def p_async_stmt(p):
    '''async_stmt : ASYNC function_stmt'''
    p[0] = Async_Node(func=p[2])

def p_await_expr(p):
    '''await_expr : AWAIT expression'''
    p[0] = Await_Node(expr=p[2])

# Gaff 
def p_gaff_stmt(p):
    '''gaff_stmt : GAFF LBRACE ID RBRACE block'''
    p[0] = Gaff_Node(ident=p[3], gaff_block=p[5])


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

try:
    parser = yacc.yacc()
except Exception as _e:
    parser = None

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
    if parser is not None:
        result = parser.parse(data, lexer=lexer)
        print(result)
