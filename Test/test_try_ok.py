import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexicals import lexer
from parse import parser
from eval import eval_ast
from semantics import SymbolTable, Type_Infer

def test_case(code, var_name, expected_val):
    ast = parser.parse(code, lexer=lexer)
    symtab = SymbolTable()
    inferrer = Type_Infer(symtab)
    inferrer.infer_program(ast)
    env = {}
    for stmt in ast:
        eval_ast(stmt, env)
    
    if var_name is not None:
        actual_val = env.get(var_name)
        val = actual_val.data if hasattr(actual_val, 'data') else actual_val
        assert val == expected_val, f"Failed for {var_name} expected {expected_val} got {val}"
    print(f"Passed : '{var_name}' == {expected_val}")

if __name__ == "__main__":
    # Variant 1: ok? [is_ok, err]
    code1 = '''
    let msg = "";
    try : {
        let age = -5;
        if age < 0 {
            throw "Age cannot be negative!";
        }
    } ok? [is_ok, err]: {
        if !is_ok {
            msg = err;
        }
    }
    '''
    test_case(code1, "msg", "Age cannot be negative!")

    # Variant 2: ok? [ok]
    code2 = '''
    let out = "";
    try :
        let x = 100;
        if x < 100 {
            throw "error message print";
        }
    ok? [ok] :
        if ok {
            out = "Success!";
        }
    '''
    test_case(code2, "out", "Success!")

    # Variant 3: ok? (Default parameters is_ok and err)
    code3 = '''
    let msg3 = "";
    try : 
        let age = -10;
        if age < 0 {
            throw "Unbraced age error!";
        }
    ok? :
        if !is_ok {
            msg3 = err;
        }
    '''
    test_case(code3, "msg3", "Unbraced age error!")

    code4 = '''
    let msg4 = "";
    try : 
        let age = -10;
        if age < 0 {
            throw "Unbraced 2-param error!";
        }
    ok? [is_ok, err] :
        if !is_ok {
            msg4 = err;
        }
    '''
    test_case(code4, "msg4", "Unbraced 2-param error!")
