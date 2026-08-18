import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexicals import lexer
from parse import parser
from eval import eval_ast, Environment, RuntimeArray
from semantics import SymbolTable, Type_Infer
from compiler import Compiler
from vm import VM

def test_array_slicing():
    code = """
    let numbers = [10, 20, 30, 40, 50];
    let sub = numbers[1..4];
    """
    ast = parser.parse(code, lexer=lexer)
    symtab = SymbolTable()
    inferrer = Type_Infer(symtab)
    inferrer.infer_program(ast)

    # AST Eval
    env = Environment()
    for stmt in ast:
        eval_ast(stmt, env)
    sub_val = env.get("sub")
    sub_elements = sub_val.elements if isinstance(sub_val, RuntimeArray) else sub_val
    assert sub_elements == [20, 30, 40], f"Expected [20, 30, 40], got {sub_elements}"
    print("AST Eval Passed : Array slicing [1..4]")

    # VM Execution
    compiler = Compiler()
    instructions = compiler.compile(ast)
    vm = VM()
    vm.run(instructions)
    vm_sub_val = vm.env.get("sub")
    vm_sub_elements = vm_sub_val.elements if isinstance(vm_sub_val, RuntimeArray) else vm_sub_val
    assert vm_sub_elements == [20, 30, 40], f"VM Expected [20, 30, 40], got {vm_sub_elements}"
    print("VM Passed : Array slicing [1..4]")

def test_string_slicing():
    code = """
    let greeting = "Hello Graff";
    let sub_str = greeting[0..5];
    """
    ast = parser.parse(code, lexer=lexer)
    symtab = SymbolTable()
    inferrer = Type_Infer(symtab)
    inferrer.infer_program(ast)

    # AST Eval
    env = Environment()
    for stmt in ast:
        eval_ast(stmt, env)
    assert env.get("sub_str") == "Hello", f"Expected 'Hello', got {env.get('sub_str')}"
    print("AST Eval Passed : String slicing [0..5]")

    # VM Execution
    compiler = Compiler()
    instructions = compiler.compile(ast)
    vm = VM()
    vm.run(instructions)
    assert vm.env.get("sub_str") == "Hello", f"VM Expected 'Hello', got {vm.env.get('sub_str')}"
    print("VM Passed : String slicing [0..5]")

if __name__ == "__main__":
    test_array_slicing()
    test_string_slicing()
