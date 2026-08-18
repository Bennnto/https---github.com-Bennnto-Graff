from parse import parser
from lexicals import lexer
from semantics import SymbolTable, Type_Infer
from compiler import Compiler
from vm import VM
from eval import eval_ast
try:
    import jitto
except ImportError:
    jitto = None
from jitto_adapter import JittoASTAdapter

def count_open_delimiters(code_str):
    """Calculates unbalanced open braces, parentheses, and brackets"""
    open_curly = code_str.count('{') - code_str.count('}')
    open_paren = code_str.count('(') - code_str.count(')')
    open_bracket = code_str.count('[') - code_str.count(']')
    return open_curly + open_paren + open_bracket

def repl():
    print("==================================================")
    print("  Welcome to Veln Bytecode VM Interactive Shell")
    print("  Commands: ':trace' or ':debug' to toggle memory visualization")
    print("            ':jit' to toggle JIT execution mode")
    print("  Type 'exit' or Ctrl+D to quit")
    print("==================================================\n")

    symtab = SymbolTable()
    compiler = Compiler()
    vm = VM()                # ✅ VM instance (lowercase 'vm')

    buffer = ""              # ✅ Define buffer BEFORE loop
    debug_mode = False       # ✅ Define debug_mode BEFORE loop
    use_jit = True           # ✅ JIT Mode DEFAULT ON 🟢 (toggle with :jit)

    while True:
        try:
            prompt = '...  ' if buffer.strip() else 'veln> '
            line = input(prompt)

            # 1. Handle REPL commands BEFORE buffering or parsing
            if not buffer.strip():
                cmd = line.strip().lower()
                if cmd == 'exit':
                    print("Goodbye!")
                    break
                elif cmd in (':trace', ':debug'):
                    debug_mode = not debug_mode
                    status = "ON 🟢" if debug_mode else "OFF 🔴"
                    print(f"Memory Step Visualization: {status}\n")
                    continue  # Skip parser for REPL commands!
                elif cmd == ':jit':
                    use_jit = not use_jit
                    status = "ON 🟢 (JIT Engine)" if use_jit else "OFF 🔴 (Standard VM)"
                    print(f"Native JIT Mode: {status}\n")
                    continue

            buffer += line + "\n"

            if count_open_delimiters(buffer) > 0:
                continue

            code_to_eval = buffer.strip()
            buffer = ""

            if not code_to_eval:
                continue

            # 2. Parse & Compile
            ast = parser.parse(code_to_eval, lexer=lexer)
            if not ast:
                continue

            inferrer = Type_Infer(symtab)
            inferrer.infer_program(ast)

            # 3. Execute
            if use_jit:
                result = JittoASTAdapter.execute(ast, vm.env)
            else:
                instructions = compiler.compile(ast)
                result = vm.run(instructions, debug=debug_mode)

            if result is not None:
                print(f"=> {result}")

        except (EOFError, KeyboardInterrupt):
            print("\nExiting Veln REPL...")
            break
        except Exception as e:
            buffer = ""
            print(f"Error: {e}")

if __name__ == "__main__":
    repl()
