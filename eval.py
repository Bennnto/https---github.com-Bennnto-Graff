from parse import (Assign_Node, Int_Node, Type_Node, BinOps_Node, Str_Node, 
                   SingleOps_Node, Variable_Node
                   )


env = []
class SemanticError(Exception):
    pass
def eval_ast(node, env, in_loop=False):
    if isinstance(node, Int_Node):
        return eval_ast(node.value, env)
    
    elif isinstance(node, Str_Node):
        return eval_ast(node.value, env)
    
    elif isinstance(node, Assign_Node):
        if node.ident in env :
            raise SemanticError(f"variable {node.ident} already defined")
        value = eval_ast(node.value, env)
        env[node.ident] = value # Store the binding in env
        return value 
    
    elif isinstance(node, Type_Node):
        return eval_ast(node.type, env)

    elif isinstance(node, BinOps_Node):
        left = eval_ast(node.left, env)
        right = eval_ast(node.right, env)
        if node.ops == "+":
            return left + right
        elif node.ops == "-":
            return left - right
        elif node.ops == "*":
            return left * right
        elif node.ops == "/":
            if right == 0 :
                raise ZeroDivisionError(f"Error : Division by zero not allowed")
            return left / right   
        elif node.ops == "%":
            if right == 0 :
                raise ZeroDivisionError(f"Error : Division by zero not allowed")
            return left % right
        elif node.ops == "**":
            return left ** right 
        elif node.ops == ">":
            return left > right
        elif node.ops == "<":
            return left < right
        elif node.ops == ">=":
            return left >= right
        elif node.ops == "<=":
            return left <= right
        elif node.ops == "!=":
            return left != right
        elif node.ops == "==":
            return left == right
    
    elif isinstance(node, Variable_Node):
        
    elif isinstance(node, SingleOps_Node):
        
    
