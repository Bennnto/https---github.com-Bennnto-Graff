from email import encoders
from email import encoders
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from environment import Environment
from lexicals import lexer
from parse import parser
from eval import eval_ast
from semantics import SymbolTable, Type_Infer

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
        assert actual_val == expected_val, f"Failed for {var_name} expected {expected_val} got {actual_val}"
    print(f"Passed : '{var_name}' == {expected_val}")


def test_const():
    # Test 1: Verify constant declaration and re-assignment prevention
    code1 = """
    fix x:int = 2
    """
    run_test_case(code1, "x", 2)
    # Verify that reassigning raises RuntimeError
    try:
        run_test_case("fix x:int = 2\nlet x = 5", "x", 2)
        assert False, "Expected RuntimeError when reassigning fix variable"
    except RuntimeError:
        print("Passed : Reassigning 'fix' variable correctly raised RuntimeError")

    code2 =("""
    fix pi:float = 3.1415
    fn circ:float[r:float]{   
        return 2.0 * pi * r;
    }
    let x:float = circ(10.0);
    """)
    run_test_case(code2, "x", 62.830000000000005)

if __name__ == "__main__":
    test_const()