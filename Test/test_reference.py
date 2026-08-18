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

def test_reference():
    # Test 1: immutable ref and deref
    code1 = '''
    let x: int = 5;
    let r = <x>;
    let z = >r<;
    '''
    run_test_case(code1, "z", 5)

    # Test 2: mutable ref and deref assign
    code2 = '''
    let x: int = 10;
    let mr = *<x>;
    >mr< = 99;
    '''
    run_test_case(code2, "x", 99)

    # Test 3: box and deref
    code3 = '''
    let b = box(42);
    let v = >b<;
    '''
    run_test_case(code3, "v", 42)

    # Test 4: move ownership
    code4 = '''
    let a: int = 7;
    let b = move a;
    '''
    run_test_case(code4, "b", 7)

if __name__ == "__main__":
    test_reference()