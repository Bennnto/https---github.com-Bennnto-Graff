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
        # Timelines store history as a list.
        # Unwrap to current value only when the expected is a scalar, not a list.
        if isinstance(actual_val, list) and not isinstance(expected_val, list):
            actual_val = actual_val[-1]
        assert actual_val == expected_val, f"Failed for {var_name} expected {expected_val} got {actual_val}"
    print(f"Passed : '{var_name}' == {expected_val}")

def test_rollback():
    code1 = """
    let timeline x : int = 5 
    x = 10
    x = 20
    x = 25
    rollback x@1
    
    """
    run_test_case(code1, 'x', 10)

    code2 ="""
    let timeline y : int = 10
    y = 15
    y = 20 
    y = 100
    y.history()
    rollback y@3
    """
    run_test_case(code2, 'y', 100)

if __name__ == "__main__":
    test_rollback()