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

def test_lambda():
    # Test 1: single-arg lambda with type annotations
    code1 = """
    let y = lambda (x:int): int -> x + 3;
    let z = y(5);
    """
    run_test_case(code1, "z", 8)

    # Test 2: single-arg lambda without return-type annotation
    code2 = """
    let doubler = lambda (n) -> n * 2;
    let r = doubler(15);
    """
    run_test_case(code2, "r", 30)

    # Test 3: multi-arg lambda
    code3 = """
    let add = lambda (x, y) -> x + y;
    let s = add(6, 7);
    """
    run_test_case(code3, "s", 13)

    # Test 4: no-parameter lambda
    code4 = """
    let fortytwo = lambda () -> 42;
    let n = fortytwo();
    """
    run_test_case(code4, "n", 42)

if __name__ == "__main__":
    test_lambda()