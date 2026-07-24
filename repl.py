from parse import parser
from lexicals import lexer
from semantics import SymbolTable, Type_Infer
from eval import eval_ast

def repl():
    print(f"Welcome to Veln Interactive Scripting Shell")
    print(f"To exit type 'exit' or Ctrl+D at the prompt")

    env = {}
    symtab = SymbolTable()
    while True:
        try:
            code_input = input('veln>').strip()
            if not code_input :
                continue
            if code_input.lower() == 'exit':
                break

            ast = parser.parse(code_input, lexer=lexer)
            if not ast :
                continue

            inferrer = Type_Infer(symtab)
            inferrer.infer_program(ast)

            for stmt in ast :
                result = eval_ast(stmt, env)
                if result is not None:
                    print(f"=> {result}")
        except Exception as e:
            print(f"Error {e}")
            

if __name__ == "__main__":
    repl()