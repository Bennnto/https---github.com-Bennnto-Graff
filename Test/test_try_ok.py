import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexicals import lexer
from parse import parser
from eval import eval_ast
from semantics import SymbolTable, Type_Infer

def run_test_case(code, var_name, expected_val):
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

def test_try_ok():
    # Variant 1: ok? [is_ok, err]
    code1 = '''
    let msg = "";
    try : {
        let is_neg = true;
        match (is_neg) :
            case (true) : { throw "Age cannot be negative!"; }
            case (_)    : { let x = 0; }
    } ok? [is_ok, err]: {
        match (is_ok) :
            case (false) : { msg = err; }
            case (_)     : { let y = 0; }
    }
    '''
    run_test_case(code1, "msg", "Age cannot be negative!")

    # Variant 2: ok? [ok]
    code2 = '''
    let out = "";
    try : {
        let is_err = false;
        match (is_err) :
            case (true) : { throw "error message print"; }
            case (_)    : { let x = 0; }
    } ok? [ok] : {
        match (ok) :
            case (true) : { out = "Success!"; }
            case (_)    : { let y = 0; }
    }
    '''
    run_test_case(code2, "out", "Success!")

    # Variant 3: ok? (Default parameters is_ok and err)
    code3 = '''
    let msg3 = "";
    try : {
        let is_neg = true;
        match (is_neg) :
            case (true) : { throw "Unbraced age error!"; }
            case (_)    : { let x = 0; }
    } ok? : {
        match (is_ok) :
            case (false) : { msg3 = err; }
            case (_)     : { let y = 0; }
    }
    '''
    run_test_case(code3, "msg3", "Unbraced age error!")

    code4 = '''
    let msg4 = "";
    try : {
        let is_neg = true;
        match (is_neg) :
            case (true) : { throw "Unbraced 2-param error!"; }
            case (_)    : { let x = 0; }
    } ok? [is_ok, err] : {
        match (is_ok) :
            case (false) : { msg4 = err; }
            case (_)     : { let y = 0; }
    }
    '''
    run_test_case(code4, "msg4", "Unbraced 2-param error!")

if __name__ == "__main__":
    test_try_ok()
