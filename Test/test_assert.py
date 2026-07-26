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
    let x = 10;
    assert x > 0;
    assert_eq x, 10;
    let res = "Passed";
    '''
    test_case(code1, "res", "Passed")

    code2 = '''
    let caught_msg = "";
    try :
        assert 2 + 2 == 5, "Math assertion failed!";
    ok? :
        if !is_ok {
            caught_msg = err;
        }
    '''
    test_case(code2, "caught_msg", "Assertion Error: Math assertion failed!")
