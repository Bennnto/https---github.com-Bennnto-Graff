import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from parse import parser
from lexicals import lexer
from semantics import check, SymbolTable
from eval import eval_ast
from compiler import Compiler
from vm import VM

def test_std_math_multi_symbol_vm():
    code = 'bind "std::Math" :: { sin, sqrt }; let r1 = sin(0.0); let r2 = sqrt(16.0);'
    ast = parser.parse(code, lexer=lexer)
    
    # Semantic check
    symtab = SymbolTable()
    for stmt in ast:
        check(stmt, symtab)
    print("Passed Semantics: Standard Math library import type-checked successfully!")

    # AST Eval
    env = {}
    for stmt in ast:
        eval_ast(stmt, env)
    assert env.get("r1") == 0.0, f"AST Expected r1=0.0, got {env.get('r1')}"
    assert env.get("r2") == 4.0, f"AST Expected r2=4.0, got {env.get('r2')}"
    print("Passed AST Eval: Standard Math library functions evaluated successfully!")

    # VM Execution
    compiler = Compiler()
    instructions = compiler.compile(ast)
    vm = VM()
    vm.run(instructions)
    assert vm.env.get("r1") == 0.0, f"VM Expected r1=0.0, got {vm.env.get('r1')}"
    assert vm.env.get("r2") == 4.0, f"VM Expected r2=4.0, got {vm.env.get('r2')}"
    print("Passed VM Execution: Standard Math library bound and executed successfully on VM!")

def test_std_math_alias_vm():
    code = 'bind "std::Math" :: Math; let r = Math.sqrt(25.0);'
    ast = parser.parse(code, lexer=lexer)
    
    # VM Execution
    compiler = Compiler()
    instructions = compiler.compile(ast)
    vm = VM()
    vm.run(instructions)
    assert vm.env.get("r") == 5.0, f"VM Expected r=5.0, got {vm.env.get('r')}"
    print("Passed VM Execution: Module alias method call Math.sqrt(25.0) executed successfully!")

def test_std_string_vm():
    code = 'bind "std::String" :: { to_upper, trim }; let greeting = to_upper("  hello world  ");'
    ast = parser.parse(code, lexer=lexer)
    compiler = Compiler()
    instructions = compiler.compile(ast)
    vm = VM()
    vm.run(instructions)
    assert vm.env.get("greeting") == "  HELLO WORLD  ", f"VM Expected uppercase string, got {vm.env.get('greeting')}"
    print("Passed VM Execution: Standard String functions executed successfully!")

if __name__ == "__main__":
    test_std_math_multi_symbol_vm()
    test_std_math_alias_vm()
    test_std_string_vm()
