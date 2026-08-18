import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexicals import lexer
from parse import parser
from eval import eval_ast
from semantics import SymbolTable, Type_Infer
from environment import Environment

def run_test_case(code, var_name, expected_val):
    ast = parser.parse(code, lexer=lexer)
    symtab = SymbolTable()
    inferrer = Type_Infer(symtab)
    inferrer.infer_program(ast)
    env = Environment()
    for stmt in ast:
        eval_ast(stmt, env)
    
    if var_name is not None:
        actual_val = env.get(var_name)
        val = actual_val.data if hasattr(actual_val, 'data') else actual_val
        assert val == expected_val, f"Failed for {var_name} expected {expected_val} got {val}"
    print(f"Passed : '{var_name}' == {expected_val}")

def test_str_interpolation():
    # Test 1: Variable interpolation
    code1 = """
    let name = "Ben";
    let msg = $"Hello {name}";
    """
    run_test_case(code1, "msg", "Hello Ben")

    # Test 2: Expression interpolation
    code2 = """
    let a = 10;
    let b = 5;
    let msg = $"Sum is {a + b}";
    """
    run_test_case(code2, "msg", "Sum is 15")

    # Test 3: Multiple placeholders
    code3 = """
    let x = 3;
    let y = 4;
    let msg = $"{x} + {y} = {x + y}";
    """
    run_test_case(code3, "msg", "3 + 4 = 7")

if __name__ == "__main__":
    test_str_interpolation()