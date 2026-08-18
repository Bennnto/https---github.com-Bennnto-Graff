import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexicals import lexer
from parse import parser
from eval import eval_ast
from semantics import SymbolTable, Type_Infer
from compiler import Compiler
from vm import VM

def test_bind_pub_eval():
    module_filename = "math_temp.vl"
    module_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), module_filename)
    with open(module_path, "w", encoding="utf-8") as f:
        f.write('''
        pub fn add[a: int, b: int] {
            return a + b;
        }
        pub fn mul[a: int, b: int] {
            return a * b;
        }
        ''')

    try:
        # Test 1: Quoted import single alias
        code1 = f'bind "{module_filename}" :: add; let res1 = add(10, 20);'
        ast1 = parser.parse(code1, lexer=lexer)
        symtab1 = SymbolTable()
        Type_Infer(symtab1).infer_program(ast1)
        env1 = {}
        for stmt in ast1:
            eval_ast(stmt, env1)
        assert env1.get("res1") == 30, f"Expected 30, got {env1.get('res1')}"

        # Test 2: Unquoted module path (math_temp.vl) and wildcard * import
        code2 = 'bind math_temp.vl :: *; let res2 = add(5, 5); let res3 = mul(3, 4);'
        ast2 = parser.parse(code2, lexer=lexer)
        symtab2 = SymbolTable()
        Type_Infer(symtab2).infer_program(ast2)
        
        env2 = {}
        for stmt in ast2:
            eval_ast(stmt, env2)
        assert env2.get("res2") == 10, f"Expected 10, got {env2.get('res2')}"
        assert env2.get("res3") == 12, f"Expected 12, got {env2.get('res3')}"

        # Test 3: Multi-symbol import syntax bind math_temp.vl :: { add, mul }
        code3 = 'bind math_temp.vl :: { add, mul }; let res4 = add(100, 200); let res5 = mul(10, 10);'
        ast3 = parser.parse(code3, lexer=lexer)
        symtab3 = SymbolTable()
        Type_Infer(symtab3).infer_program(ast3)

        # AST Eval Test
        env3 = {}
        for stmt in ast3:
            eval_ast(stmt, env3)
        assert env3.get("res4") == 300, f"Expected 300, got {env3.get('res4')}"
        assert env3.get("res5") == 100, f"Expected 100, got {env3.get('res5')}"
        print("Passed AST Eval: Multi-symbol bind math_temp.vl :: { add, mul } works!")

        # VM Execution Test
        compiler = Compiler()
        instructions = compiler.compile(ast3)
        vm = VM()
        vm.run(instructions)
        assert vm.env.get("res4") == 300, f"VM: Expected 300, got {vm.env.get('res4')}"
        assert vm.env.get("res5") == 100, f"VM: Expected 100, got {vm.env.get('res5')}"
        print("Passed VM Execution: Multi-symbol bind math_temp.vl :: { add, mul } works!")

    finally:
        if os.path.exists(module_path):
            os.remove(module_path)

if __name__ == "__main__":
    test_bind_pub_eval()
