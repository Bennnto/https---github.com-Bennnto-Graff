"""
Comprehensive JIT Test Suite for all new_eval syntax features using JittoASTAdapter
"""

import sys
import os
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, 'src'))
sys.path.insert(0, os.path.join(ROOT_DIR, 'addons'))
sys.path.insert(0, os.path.join(ROOT_DIR, 'cli'))

from parse import parser
from lexicals import lexer
from semantics import SymbolTable, Type_Infer
from eval import Environment
from jitto_adapter import JittoASTAdapter

def run_jit_test(code_str, target_var=None, expected_val=None):
    ast = parser.parse(code_str, lexer=lexer)
    symtab = SymbolTable()
    inferrer = Type_Infer(symtab)
    inferrer.infer_program(ast)

    env = Environment()
    res = JittoASTAdapter.execute(ast, env)

    if target_var is not None:
        actual_val = env.get(target_var)
        val = actual_val[-1] if isinstance(actual_val, list) else (actual_val.data if hasattr(actual_val, 'data') else actual_val)
        assert val == expected_val, f"JIT Error: expected {expected_val}, got {val}"
        print(f"  ✅ [JIT PASSED] {target_var} == {expected_val}")
    else:
        print(f"  ✅ [JIT PASSED] Executed successfully, result = {res}")

def test_all_jit_features():
    print("==================================================")
    print("  Running Full JIT Test Suite Across All Syntax")
    print("==================================================")

    # 1. Arithmetic & BinOps
    print("\n--- 1. Arithmetic & BinOps ---")
    run_jit_test("let x = 10; let y = 20; let z = (x + y) * 2;", "z", 60)
    run_jit_test("let a = 100; let b = 4; let res = a / b;", "res", 25)

    # 2. Variables & Fix Const
    print("\n--- 2. Variables & Fix Const ---")
    run_jit_test("fix MAX: int = 500;", "MAX", 500)

    # 3. Enum & Struct
    print("\n--- 3. Enum & Struct ---")
    run_jit_test("""
        enum Status: PENDING APPROVED REJECTED
        let s = Status.APPROVED;
    """, "s", 1)

    run_jit_test("""
        struct Point { x: int, y: int }
        let p = Point { x: 10, y: 20 };
        let px = p.x;
    """, "px", 10)

    # 4. Functions
    print("\n--- 4. Functions ---")
    run_jit_test("""
        fn mult: int [a: int, b: int] {
            return a * b;
        }
        let ans = mult(6, 7);
    """, "ans", 42)

    # 5. Timeline & Rollback
    print("\n--- 5. Timeline & Rollback ---")
    run_jit_test("""
        let timeline x = 10
        x = 20
        rollback x@0
    """, "x", 10)

    print("\n==================================================")
    print("  🎉 All Syntax Constructs Successfully Passed JIT!")
    print("==================================================")

if __name__ == "__main__":
    test_all_jit_features()
