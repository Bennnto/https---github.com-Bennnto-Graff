import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexicals import lexer
from parse import parser
from eval import eval_ast, Environment
from semantics import SymbolTable, Type_Infer
from compiler import Compiler
from vm import VM

def run_test_eval(code, var_name, field_name, expected_val):
    ast = parser.parse(code, lexer=lexer)
    symtab = SymbolTable()
    inferrer = Type_Infer(symtab)
    inferrer.infer_program(ast)
    env = Environment()
    for stmt in ast:
        eval_ast(stmt, env)
    
    struct_obj = env.get(var_name)
    actual_val = struct_obj.fields.get(field_name)
    assert actual_val == expected_val, f"AST Eval Failed for {var_name}.{field_name}: expected {expected_val}, got {actual_val}"
    print(f"AST Eval Passed : '{var_name}.{field_name}' == {expected_val}")

def run_test_vm(code, var_name, field_name, expected_val):
    ast = parser.parse(code, lexer=lexer)
    symtab = SymbolTable()
    inferrer = Type_Infer(symtab)
    inferrer.infer_program(ast)
    
    compiler = Compiler()
    instructions = compiler.compile(ast)
    vm = VM()
    vm.run(instructions)
    
    struct_obj = vm.env.get(var_name)
    actual_val = struct_obj.fields.get(field_name)
    assert actual_val == expected_val, f"VM Failed for {var_name}.{field_name}: expected {expected_val}, got {actual_val}"
    print(f"VM Passed : '{var_name}.{field_name}' == {expected_val}")

def test_struct():
    code = """
    struct Point {
        x: int,
        y: int
    }
    let p = Point{ x: 10, y: 20 };
    """
    run_test_eval(code, "p", "x", 10)
    run_test_eval(code, "p", "y", 20)
    
    run_test_vm(code, "p", "x", 10)
    run_test_vm(code, "p", "y", 20)

if __name__ == "__main__":
    test_struct()
