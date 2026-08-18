import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexicals import lexer
from parse import parser
from eval import eval_ast
from semantics import SymbolTable, Type_Infer
from compiler import Compiler
from vm import VM

def test_stdlib_modules():
    code = '''
    bind std::math :: { sin, sqrt, floor };
    bind std::string :: { to_upper, trim, len };
    bind std::array :: { push, pop };
    bind std::file :: { write, read, exists, remove };
    bind std::stat :: { mean, median };
    bind std::time :: { now, year };
    bind std::sys :: { platform };
    bind std::crypto :: { sha256 };

    let s1 = sqrt(16);
    let f1 = floor(4.9);
    let u1 = to_upper("hello");
    let l1 = len("world");
    let hash1 = sha256("veln");
    let m1 = mean([10, 20, 30]);
    '''

    ast = parser.parse(code, lexer=lexer)

    # 1. Semantics Check
    symtab = SymbolTable()
    inferrer = Type_Infer(symtab)
    inferrer.infer_program(ast)

    # 2. AST Evaluation Check
    env = {}
    for stmt in ast:
        eval_ast(stmt, env)

    assert env.get("s1") == 4.0, f"Expected 4.0, got {env.get('s1')}"
    assert env.get("f1") == 4, f"Expected 4, got {env.get('f1')}"
    assert env.get("u1") == "HELLO", f"Expected HELLO, got {env.get('u1')}"
    assert env.get("l1") == 5, f"Expected 5, got {env.get('l1')}"
    assert env.get("m1") == 20.0, f"Expected 20.0, got {env.get('m1')}"
    assert len(env.get("hash1")) == 64, f"Expected SHA256 length 64, got {len(env.get('hash1'))}"
    print("Passed AST Eval: Standard Library modules working!")

    # 3. Bytecode VM Check
    compiler = Compiler()
    instructions = compiler.compile(ast)
    vm = VM()
    vm.run(instructions)

    assert vm.env.get("s1") == 4.0, f"VM: Expected 4.0, got {vm.env.get('s1')}"
    assert vm.env.get("u1") == "HELLO", f"VM: Expected HELLO, got {vm.env.get('u1')}"
    assert vm.env.get("m1") == 20.0, f"VM: Expected 20.0, got {vm.env.get('m1')}"
    print("Passed VM Execution: Standard Library modules working!")

if __name__ == "__main__":
    test_stdlib_modules()
