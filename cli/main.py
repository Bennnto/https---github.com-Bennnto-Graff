"""
Gaff Programming Language CLI Entrypoint
Run scripts with Native Codegen compilation and execution by default.
"""

import sys
import os
import subprocess

from parse import parser
from lexicals import lexer
from semantics import SymbolTable, Type_Infer, insert_auto_drop
from native_codegen import NativeCodegen
import manifest
import repl
import error_reporter

GAFF_VERSION = "1.0.0 (Native Codegen Release)"

def get_manifest_path():
    if os.path.exists("project.graff"):
        return "project.graff"
    return "project.gf"

def run_script(filepath, use_manifest=True):
    if not os.path.exists(filepath):
        print(f"Error: Gaff source file '{filepath}' not found.")
        sys.exit(1)

    with open(filepath, "r", encoding="utf-8") as f:
        code = f.read()

    ast = parser.parse(code, lexer=lexer)
    if not ast:
        print(f"Error: Failed to parse Gaff script '{filepath}'.")
        sys.exit(1)

    symtab = SymbolTable()
    try:
        Type_Infer(symtab).infer_program(ast)
        ast = insert_auto_drop(ast)
    except Exception as e:
        line_no = getattr(e, 'lineno', 1)
        err_msg = error_reporter.format_error(filepath, code, line_no, 0, str(e), error_type="Type Error")
        print(err_msg)
        sys.exit(1)

    os.makedirs("dist", exist_ok=True)
    base_name = os.path.splitext(os.path.basename(filepath))[0]
    c_path = os.path.join("dist", f"{base_name}.c")
    output_binary = os.path.join("dist", base_name)

    codegen = NativeCodegen()
    c_code = codegen.generate(ast, main_name="main")
    with open(c_path, "w", encoding="utf-8") as f:
        f.write(c_code)

    clang_bin = "/opt/homebrew/opt/llvm/bin/clang"
    if not os.path.exists(clang_bin):
        clang_bin = "clang"

    compiled = False
    try:
        res = subprocess.run([clang_bin, "-O3", c_path, "-o", output_binary, "-lm"], capture_output=True, text=True)
        if res.returncode == 0:
            compiled = True
    except FileNotFoundError:
        try:
            res = subprocess.run(["gcc", "-O3", c_path, "-o", output_binary, "-lm"], capture_output=True, text=True)
            if res.returncode == 0:
                compiled = True
        except FileNotFoundError:
            pass

    if compiled and os.path.exists(output_binary):
        subprocess.run([output_binary])
    else:
        from eval import eval_ast, Environment
        env = Environment()
        for stmt in ast:
            eval_ast(stmt, env)

def main():
    args = sys.argv[1:]

    if not args:
        manifest_file = get_manifest_path()
        if os.path.exists(manifest_file):
            env, config = manifest.load_manifest(manifest_file)
            entry_file = config.get("entry", "main.gf")
            run_script(entry_file, use_manifest=True)
        else:
            repl.repl()
        return

    cmd = args[0]

    if cmd in ("--version", "-v"):
        print(f"Gaff Language Version: {GAFF_VERSION}")

    elif cmd == "repl":
        repl.repl()

    elif cmd == "run":
        target = args[1] if len(args) > 1 else "main.gf"
        run_script(target, use_manifest=True)

    else:
        # Treat first arg as script filepath
        run_script(cmd, use_manifest=True)

if __name__ == "__main__":
    main()
