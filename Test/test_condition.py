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

def test_condition():
    # Test 1: Match boolean condition (true case)
    run_test_case("let res = 0; match (10 > 5) : case (true) : { res = 1; } case (false) : { res = 2; }", "res", 1)
    
    # Test 2: Match boolean condition (false case)
    run_test_case("let res = 0; match (2 > 5) : case (true) : { res = 1; } case (false) : { res = 2; }", "res", 2)
    
    # Test 3: Match value with wildcard (_)
    run_test_case("let res = 0; let x = 5; match (x) : case (1) : { res = 10; } case (_) : { res = 99; }", "res", 99)
    
    # Test 4: While loop check
    run_test_case("let count = 0; while (count < 5) { count = count + 1; }", "count", 5)
    run_test_case("let sum = 0; let i = 1; while (i <= 4) { sum = sum + i; i = i + 1; }", "sum", 10)

    run_test_case("""
    let y = 0
    let x = 5
    match(x):
        case(2): { y = 5 }
        case(3): { y = 5 } 
        case(5): { y = 10 }
        case(_): { y = 100 } 
    """, "y", 10)

if __name__ == "__main__":
    test_condition()