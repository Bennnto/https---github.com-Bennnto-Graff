import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from parse import parser
from lexicals import lexer
from semantics import check, SymbolTable
from eval import eval_ast
from compiler import Compiler
from vm import VM

def test_for_range_two_args():
    # Range without step: 1..5 (step is None) -> iterations for 1, 2, 3, 4
    code = 'let sum = 0; for i in 1..5 { sum = sum + i; }'
    ast = parser.parse(code, lexer=lexer)
    
    # Semantic Analysis
    symtab = SymbolTable()
    for stmt in ast:
        check(stmt, symtab)
    print("Passed Semantics: Range_Node without step type-checked successfully!")

    # AST Evaluation
    env = {}
    for stmt in ast:
        eval_ast(stmt, env)
    assert env.get("sum") == 10, f"Expected sum=10 (1+2+3+4), got {env.get('sum')}"
    print("Passed AST Eval: Range_Node (1..5 without step) evaluated correctly to 10!")

    # VM Execution
    compiler = Compiler()
    instructions = compiler.compile(ast)
    vm = VM()
    vm.run(instructions)
    assert vm.env.get("sum") == 10, f"VM Expected sum=10, got {vm.env.get('sum')}"
    print("Passed VM Execution: Range_Node (1..5 without step) compiled and executed successfully!")

def test_for_range_three_args():
    # Range with step: 1..10, 2 (step is 2) -> iterations for 1, 3, 5, 7, 9
    code = 'let sum = 0; for i in 1..10, 2 { sum = sum + i; }'
    ast = parser.parse(code, lexer=lexer)
    
    # Semantic Analysis
    symtab = SymbolTable()
    for stmt in ast:
        check(stmt, symtab)
    print("Passed Semantics: Range_Node with step=2 type-checked successfully!")

    # VM Execution
    compiler = Compiler()
    instructions = compiler.compile(ast)
    vm = VM()
    vm.run(instructions)
    assert vm.env.get("sum") == 25, f"VM Expected sum=25, got {vm.env.get('sum')}"
    print("Passed VM Execution: Range_Node (1..10, 2 with step=2) compiled and executed successfully!")

if __name__ == "__main__":
    test_for_range_two_args()
    test_for_range_three_args()
