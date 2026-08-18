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

def test_generics():
    # Test 1: Generic struct with int type parameter Wrapper::<int>
    code1 = """
    struct Wrapper<T> {
        value: T
    }
    let w1 = Wrapper::<int>{ value: 42 };
    """
    run_test_eval(code1, "w1", "value", 42)
    run_test_vm(code1, "w1", "value", 42)

    # Test 2: Generic struct with string type parameter Wrapper::<str>
    code2 = """
    struct Wrapper<T> {
        value: T
    }
    let w2 = Wrapper::<str>{ value: "Hello Generics" };
    """
    run_test_eval(code2, "w2", "value", "Hello Generics")
    run_test_vm(code2, "w2", "value", "Hello Generics")

if __name__ == "__main__":
    test_generics()
