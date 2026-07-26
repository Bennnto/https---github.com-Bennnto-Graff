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
    # Test 1: Succeeds on retry 2
    code1 = '''
    let count = 0;
    let status = "";
    attempt(3) : {
        count = count + 1;
        if count < 2 {
            throw "Error on first attempt!";
        }
        status = "Success on attempt 2";
    } fallback : {
        status = "Fallback triggered";
    }
    '''
    test_case(code1, "status", "Success on attempt 2")

    # Test 2: Fails all retries and executes fallback
    code2 = '''
    let res = "";
    attempt(2) : {
        throw "Persistent error";
    } fallback : {
        res = "Fallback executed";
    }
    '''
    test_case(code2, "res", "Fallback executed")
