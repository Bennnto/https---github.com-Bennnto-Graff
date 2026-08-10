import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from lexicals import lexer
from parse import parser
from native_codegen import NativeCodegen

def test_gaff_node_codegen():
    # 1. We write a sample program using our gaff constraint
    code = """
    let x = 10;
    gaff { x } {
        x > 0;
    }
    x = -5;
    """
    
    # 2. We parse it into an AST
    ast = parser.parse(code, lexer=lexer)
    
    # 3. We run our NativeCodegen on it!
    codegen = NativeCodegen()
    c_code = codegen.generate(ast)
    
    print("--- GENERATED C CODE ---")
    print(c_code)
    print("------------------------")
    
    # 4. We verify that our new C logic is in the generated output!
    assert "bool gaff_check_x" in c_code, "Failed: C function for constraint was not generated!"
    assert "return (x > 0)" in c_code or "return x > 0" in c_code, "Failed: Constraint logic missing from function!"
    assert "if(!gaff_check_x" in c_code or "if (!gaff_check_x" in c_code, "Failed: Assignment constraint check missing!"
    
    print("Passed : Gaff Constraint C Code Generation")

if __name__ == "__main__":
    test_gaff_node_codegen()
