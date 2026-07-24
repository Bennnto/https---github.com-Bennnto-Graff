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
        assert actual_val == expected_val, f"Failed for {var_name} expected {expected_val} got {actual_val}"
    print(f"Passed : '{var_name}' == {expected_val}")

if __name__ == "__main__":
    test_case("let x:int = 5", "x", 5)
    test_case("let x:str = '5'", "x", '5')
    test_case("let y:int = -5234", "y", -5234)
    test_case("let z:float = -3425.34", "z", -3425.34)
    test_case("let a:float = 3.1415", "a", 3.1415)
    test_case("let b:bool = true", "b", True)
    test_case("let c:bool = false", "c", False)
    test_case("let d = 5", "d", 5)
    test_case("let f:str = 'Hello World'", "f", 'Hello World')
