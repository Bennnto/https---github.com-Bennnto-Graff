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

    code2 = '''
    let status = false;
    try : {
        let x = 100;
    } ok? [is_ok, err]: {
        status = is_ok;
    }
    '''
    test_case(code2, "status", True)

    code3 = '''
    let msg2 = "";
    try : 
        let age = -10;
        if age < 0 {
            throw "Unbraced age error!";
        }
    ok? [is_ok, err]:
        if !is_ok {
            msg2 = err;
        }
    '''
    test_case(code3, "msg2", "Unbraced age error!")
