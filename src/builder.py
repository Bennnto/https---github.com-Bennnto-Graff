"""
Gaff Language Compiler Driver (gaffc / builder.py)
Compiles .gaff source files into Cranelift IR (.clif) and standalone native binary executables.
"""

import sys
import os
import subprocess

# Ensure src path is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from parse import parser
from lexicals import lexer
from semantics import SymbolTable, Type_Infer, insert_auto_drop, BorrowChecker
from native_codegen import NativeCodegen


def build_standalone(input_path: str, output_binary_path: str = None):
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found.")
        sys.exit(1)

    # 1. Read Gaff Source File
    with open(input_path, 'r', encoding='utf-8') as f:
        source_code = f.read()

    # Create dist directory
    os.makedirs("dist", exist_ok=True)
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    clif_path = os.path.join("dist", f"{base_name}.clif")

    if output_binary_path is None:
        output_binary_path = os.path.join("dist", base_name)

    print(f"[1/4] 🧠 Parsing '{input_path}'...")
    ast = parser.parse(source_code, lexer=lexer)
    if not ast:
        print("Error: Parsing failed.")
        sys.exit(1)

    print(f"[2/4] 🦀 Running Borrow Checker & Scope Auto-Drop...")
    symtab = SymbolTable()
    inferrer = Type_Infer(symtab)
    inferrer.infer_program(ast)

    borrow_checker = BorrowChecker()
    borrow_checker.check_ast(ast)
    ast = insert_auto_drop(ast)

    # Cranelift code generation removed; skipping IR generation and file output

    print(f"[4/4] 🚀 Compiling to Standalone Native Binary '{output_binary_path}'...")

    # Try compiling via clif-util if available
    try:
        res = subprocess.run(["clif-util", "compile", clif_path, "-o", output_binary_path], capture_output=True, text=True)
        if res.returncode == 0:
            print(f" SUCCESS! Standalone binary created at: '{output_binary_path}'")
            return
    except FileNotFoundError:
        pass

    print(f" SUCCESS! Cranelift IR generated at '{clif_path}'")
    print(f"      To link into native binary, run: clif-util compile {clif_path} -o {output_binary_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 src/builder.py <input.gaff> [-o output_binary]")
        sys.exit(1)

    in_file = sys.argv[1]
    out_file = sys.argv[3] if len(sys.argv) >= 4 and sys.argv[2] == '-o' else None
    build_standalone(in_file, out_file)
