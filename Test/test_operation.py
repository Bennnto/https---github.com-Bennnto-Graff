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

def test_operation():
    run_test_case("let a = 10 + 20", "a", 30)
    run_test_case("let b = 50 - 15", "b", 35)
    run_test_case("let c = 6 * 7", "c", 42)
    run_test_case("let d = 20 / 4", "d", 5.0)
    run_test_case("let e = 17 % 5", "e", 2)
    run_test_case("let f = 2 ** 3", "f", 8)
    run_test_case("let g = 10 > 5", "g", True)
    run_test_case("let h = 10 == 10", "h", True)
    run_test_case("let i = true & false", "i", False)
    run_test_case("let j = true | false", "j", True)

if __name__ == "__main__":
    test_operation()
