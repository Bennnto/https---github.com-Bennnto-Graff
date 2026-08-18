import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from parse import parser
from lexicals import lexer
from semantics import check, SymbolTable
from eval import eval_ast
from compiler import Compiler
from vm import VM

def test_match_case_vm():
    code = '''
    let code = 404;
    let res = 0;
    match (code) :
        case (200) : { res = 1; }
        case (404) : { res = 2; }
        case (_)   : { res = 3; }
    '''
    ast = parser.parse(code, lexer=lexer)
    
    # Semantic check
    symtab = SymbolTable()
    for stmt in ast:
        check(stmt, symtab)
    print("Passed Semantics: Match_Node pattern matching type-checked successfully!")

    # AST Evaluation
    env = {}
    for stmt in ast:
        eval_ast(stmt, env)
    assert env.get("res") == 2, f"AST Expected res=2, got {env.get('res')}"
    print("Passed AST Eval: Match_Node matched case 404 successfully!")

    # VM Execution
    compiler = Compiler()
    instructions = compiler.compile(ast)
    vm = VM()
    vm.run(instructions)
    assert vm.env.get("res") == 2, f"VM Expected res=2, got {vm.env.get('res')}"
    print("Passed VM Execution: Match_Node compiled and executed pattern matching successfully!")

def test_match_wildcard_vm():
    code = '''
    let status = 500;
    let res = 0;
    match (status) :
        case (200) : { res = 1; }
        case (404) : { res = 2; }
        case (_)   : { res = 99; }
    '''
    ast = parser.parse(code, lexer=lexer)
    compiler = Compiler()
    instructions = compiler.compile(ast)
    vm = VM()
    vm.run(instructions)
    assert vm.env.get("res") == 99, f"VM Expected res=99, got {vm.env.get('res')}"
    print("Passed VM Execution: Match_Node fallback wildcard (_) matched successfully!")

if __name__ == "__main__":
    test_match_case_vm()
    test_match_wildcard_vm()
