import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexicals import lexer
from parse import parser
from eval import eval_ast, Environment
from semantics import SymbolTable, Type_Infer
from compiler import Compiler
from vm import VM

def test_default_parameters():
    code = """
    fn greet:str[name: str = "World"] {
        return $"Hello, {name}!";
    }

    let msg1 = greet();
    let msg2 = greet("Alice");
    """
    ast = parser.parse(code, lexer=lexer)
    symtab = SymbolTable()
    inferrer = Type_Infer(symtab)
    inferrer.infer_program(ast)
    
    # AST Eval
    env = Environment()
    for stmt in ast:
        eval_ast(stmt, env)
    assert env.get("msg1") == "Hello, World!", f"Expected 'Hello, World!', got {env.get('msg1')}"
    assert env.get("msg2") == "Hello, Alice!", f"Expected 'Hello, Alice!', got {env.get('msg2')}"
    print("AST Eval Passed : Default parameters")

    # VM Execution
    compiler = Compiler()
    instructions = compiler.compile(ast)
    vm = VM()
    vm.run(instructions)
    assert vm.env.get("msg1") == "Hello, World!", f"VM Expected 'Hello, World!', got {vm.env.get('msg1')}"
    assert vm.env.get("msg2") == "Hello, Alice!", f"VM Expected 'Hello, Alice!', got {vm.env.get('msg2')}"
    print("VM Passed : Default parameters")

def test_fstring_format_specifiers():
    code = """
    fix pi: float = 3.14159265;
    let formatted_pi = $"Pi: {pi:.2f}";
    let count: int = 7;
    let padded_count = $"Count: {count:03d}";
    """
    ast = parser.parse(code, lexer=lexer)
    symtab = SymbolTable()
    inferrer = Type_Infer(symtab)
    inferrer.infer_program(ast)

    # AST Eval
    env = Environment()
    for stmt in ast:
        eval_ast(stmt, env)
    assert env.get("formatted_pi") == "Pi: 3.14", f"Expected 'Pi: 3.14', got {env.get('formatted_pi')}"
    assert env.get("padded_count") == "Count: 007", f"Expected 'Count: 007', got {env.get('padded_count')}"
    print("AST Eval Passed : F-String format specifiers")

    # VM Execution
    compiler = Compiler()
    instructions = compiler.compile(ast)
    vm = VM()
    vm.run(instructions)
    assert vm.env.get("formatted_pi") == "Pi: 3.14", f"VM Expected 'Pi: 3.14', got {vm.env.get('formatted_pi')}"
    assert vm.env.get("padded_count") == "Count: 007", f"VM Expected 'Count: 007', got {vm.env.get('padded_count')}"
    print("VM Passed : F-String format specifiers")

def test_module_import():
    # Write a temporary helper file 'math_helper.gf'
    mod_code = """
    fn square:int[x: int] {
        return x * x;
    }
    """
    with open("math_helper.gf", "w", encoding="utf-8") as f:
        f.write(mod_code)

    main_code = """
    bind "math_helper.gf" :: math;
    let result = math.square(5);
    """
    try:
        ast = parser.parse(main_code, lexer=lexer)
        env = Environment()
        for stmt in ast:
            eval_ast(stmt, env)
        assert env.get("result") == 25, f"Expected 25, got {env.get('result')}"
        print("AST Eval Passed : Module import .gf")
    finally:
        if os.path.exists("math_helper.gf"):
            os.remove("math_helper.gf")

if __name__ == "__main__":
    test_default_parameters()
    test_fstring_format_specifiers()
    test_module_import()
