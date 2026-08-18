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
        assert actual_val == expected_val, f"Failed for {var_name} expected {expected_val} got {actual_val}"
    print(f"Passed : '{var_name}' == {expected_val}")

def test_functions():
    run_test_case("fn add: int [x: int, y: int] { return x + y; } let res = add(10, 20);", "res", 30)
    run_test_case("fn mul [a, b] { return a * b; } let res = mul(6, 7);", "res", 42)
    run_test_case("fn double [n] { return n * 2; } let res = double(15);", "res", 30)

if __name__ == "__main__":
    test_functions()
