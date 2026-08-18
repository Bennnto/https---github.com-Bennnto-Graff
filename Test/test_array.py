import os
import sys
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, 'src'))

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
        val = actual_val.elements if hasattr(actual_val, 'elements') else actual_val
        assert val == expected_val, f"Failed for {var_name} expected {expected_val} got {val}"
    print(f"Passed : '{var_name}' == {expected_val}")

def test_array():
    run_test_case("let fixed_arr: int array[3] = [10, 20, 30];", "fixed_arr", [10, 20, 30])
    run_test_case("let fixed_arr: int array[3] = [10, 20, 30]; fixed_arr[1] = 99; let val = fixed_arr[1];", "val", 99)
    run_test_case("let dyn_arr: int array = [1, 2]; dyn_arr.push(3);", "dyn_arr", [1, 2, 3])
    run_test_case("let dyn_arr: int array = [10, 20, 30]; let length = dyn_arr.len();", "length", 3)

if __name__ == "__main__":
    test_array()
