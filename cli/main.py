"""
Gaff Programming Language CLI Entrypoint
Run scripts with JIT hardware compilation by default and manifest auto-binding.
"""

import sys
import os

from parse import parser
from lexicals import lexer
from semantics import SymbolTable, Type_Infer
from jitto_adapter import JittoASTAdapter
import manifest
import repl
import error_reporter

GAFF_VERSION = "1.0.0 (with jitto JIT Engine)"

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

    manifest_file = get_manifest_path()

    if use_manifest and os.path.exists(manifest_file):
        env, config = manifest.load_manifest(manifest_file)
    else:
        from eval import Environment
        env = Environment()

    symtab = SymbolTable()
    symtab.has_wildcard = True
    for k, v in env.bindings.items():
        if k not in symtab.scopes[-1]:
            symtab.scopes[-1][k] = 'any'

    try:
        Type_Infer(symtab).infer_program(ast)
    except Exception:
        pass

    try:
        JittoASTAdapter.execute(ast, env)
    except Exception as e:
        line_no = getattr(e, 'lineno', 1)
        err_msg = error_reporter.format_error(filepath, code, line_no, 0, str(e), error_type="Execution Error")
        print(err_msg)
        sys.exit(1)

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
