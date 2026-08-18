import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from parse import parser
from lexicals import lexer
from semantics import check, SymbolTable
from eval import eval_ast
from compiler import Compiler
from vm import VM

def test_fstr_eval_and_vm():
    code = 'let name = "Ben"; let age = 25; let msg = $"Hello {name}, age is {age + 1}!";'
    ast = parser.parse(code, lexer=lexer)
    
    # Semantic check
    symtab = SymbolTable()
    for stmt in ast:
        check(stmt, symtab)
        
    # AST Evaluation
    env = {}
    for stmt in ast:
        eval_ast(stmt, env)
    assert env.get("msg") == "Hello Ben, age is 26!", f"Expected 'Hello Ben, age is 26!', got {env.get('msg')}"
    print("Passed AST Eval: Fstr_Node interpolation works!")

    # VM Execution
    compiler = Compiler()
    instructions = compiler.compile(ast)
    vm = VM()
    vm.run(instructions)
    assert vm.env.get("msg") == "Hello Ben, age is 26!", f"VM Expected 'Hello Ben, age is 26!', got {vm.env.get('msg')}"
    print("Passed VM Execution: Fstr_Node compiled and executed successfully!")

def test_index_assign_return():
    code = 'let arr = [10, 20, 30]; arr[1] = 99; let res = arr[1];'
    ast = parser.parse(code, lexer=lexer)
    env = {}
    for stmt in ast:
        eval_ast(stmt, env)
    assert env.get("res") == 99, f"Expected 99, got {env.get('res')}"
    print("Passed AST Eval: Index_Assign_Node updates array element successfully!")

if __name__ == "__main__":
    test_fstr_eval_and_vm()
    test_index_assign_return()
