import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexicals import lexer
from parse import parser
from semantics import SymbolTable, Type_Infer
from compiler import Compiler
from vm import VM

def run_test_vm(code, var_name, expected_val):
    ast = parser.parse(code, lexer=lexer)
    symtab = SymbolTable()
    inferrer = Type_Infer(symtab)
    inferrer.infer_program(ast)
    
    compiler = Compiler()
    instructions = compiler.compile(ast)
    
    vm = VM()
    vm.run(instructions)
    
    if var_name is not None:
        actual_val = vm.env.get(var_name)
        val = actual_val.data if hasattr(actual_val, 'data') else actual_val
        assert val == expected_val, f"VM Verification Failed for '{var_name}': expected {expected_val}, got {val}"
    print(f"VM Verified: '{var_name}' == {expected_val}")

def test_vm_suite():
    # 1. Variables & Arithmetic
    run_test_vm("let x = 15; let y = 25; let z = x + y;", "z", 40)
    run_test_vm("let a = 10; let b = 3; let res = a % b;", "res", 1)

    # 2. Comparisons & Logic
    run_test_vm("let x = 10; let is_gt = x > 5;", "is_gt", True)
    run_test_vm("let a = true; let b = false; let res = a & b;", "res", False)

    # 3. Enum compilation & lookup
    run_test_vm("""
    enum Status: PENDING APPROVED REJECTED
    let s = Status.APPROVED;
    """, "s", 1)

    run_test_vm("""
    enum Color: RED = 100 GREEN = 200 BLUE = 300
    let c = Color.GREEN;
    """, "c", 200)

    # 4. Functions
    run_test_vm("""
    fn add: int [a: int, b: int] {
        return a + b;
    }
    let sum = add(12, 18);
    """, "sum", 30)

if __name__ == "__main__":
    print("--- Running Compiler & VM Verification Tests ---")
    test_vm_suite()
    print("\nCompiler & VM 100% Verified Successfully!")
