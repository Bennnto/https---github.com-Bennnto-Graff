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

def test_hash():
    run_test_case('let user: hash[str, int] = {"math": 95, "english": 88};', "user", {"math": 95, "english": 88})
    run_test_case('let user: hash[str, int] = {"math": 95}; user["math"] = 100; let val = user["math"];', "val", 100)
    run_test_case('let user: hash[str, int] = {"math": 95, "english": 88}; let length = user.len();', "length", 2)
    run_test_case('let user: hash[str, str] = {"name": "Ben"}; let val = user["name"];', "val", "Ben")

if __name__ == "__main__":
    test_hash()
