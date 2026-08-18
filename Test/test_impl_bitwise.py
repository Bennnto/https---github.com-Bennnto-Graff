import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexicals import lexer
from parse import parser
from eval import eval_ast, Environment
from semantics import SymbolTable, Type_Infer
from compiler import Compiler
from vm import VM

def run_test_eval(code, var_name, expected_val):
    ast = parser.parse(code, lexer=lexer)
    symtab = SymbolTable()
    inferrer = Type_Infer(symtab)
    inferrer.infer_program(ast)
    env = Environment()
    for stmt in ast:
        eval_ast(stmt, env)
    
    actual_val = env.get(var_name)
    assert actual_val == expected_val, f"AST Eval Failed for {var_name}: expected {expected_val}, got {actual_val}"
    print(f"AST Eval Passed : '{var_name}' == {expected_val}")

def run_test_vm(code, var_name, expected_val):
    ast = parser.parse(code, lexer=lexer)
    symtab = SymbolTable()
    inferrer = Type_Infer(symtab)
    inferrer.infer_program(ast)
    
    compiler = Compiler()
    instructions = compiler.compile(ast)
    vm = VM()
    vm.run(instructions)
    
    actual_val = vm.env.get(var_name)
    assert actual_val == expected_val, f"VM Failed for {var_name}: expected {expected_val}, got {actual_val}"
    print(f"VM Passed : '{var_name}' == {expected_val}")

def test_bitwise_operators():
    code = """
    let a = 1 << 3;    # 8
    let b = 16 >> 2;   # 4
    let c = 5 ^ 3;     # 6
    let d = ~0;        # -1
    """
    run_test_eval(code, "a", 8)
    run_test_eval(code, "b", 4)
    run_test_eval(code, "c", 6)
    run_test_eval(code, "d", -1)

    run_test_vm(code, "a", 8)
    run_test_vm(code, "b", 4)
    run_test_vm(code, "c", 6)
    run_test_vm(code, "d", -1)

def test_struct_impl():
    code = """
    struct Rectangle {
        w: int,
        h: int
    }

    impl Rectangle {
        fn area:int[self] {
            return self.w * self.h;
        }
    }

    let r = Rectangle{ w: 10, h: 5 };
    let a = r.area();
    """
    run_test_eval(code, "a", 50)
    run_test_vm(code, "a", 50)

if __name__ == "__main__":
    test_bitwise_operators()
    test_struct_impl()
