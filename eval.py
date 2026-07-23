from parse import (Assign_Node, Int_Node, Type_Node, BinOps_Node, Str_Node, 
                   SingleOps_Node, Variable_Node, Bool_Node, Disp_Node, Entry_Node,
                   If_Else_Node, Break_Exception, Continue_Exception, While_Node,
                   Break_Node, Continue_Node, Return_Exception, Return_Node, Void_Node, Function_Node,
                   Call_Node, For_Node, Float_Node)

class SemanticError(Exception):
    pass

def eval_ast(node, env, in_loop=False):
    if node is None:
        return None

    if isinstance(node, Int_Node):
        return node.value
    
    elif isinstance(node, Str_Node):
        return node.value
    
    elif isinstance(node, Bool_Node):
        return node.value
    
    elif isinstance(node, Void_Node):
        return None
    
    elif isinstance(node, Float_Node):
        return node.value
    
    elif isinstance(node, Assign_Node):
        value = eval_ast(node.value, env, in_loop=in_loop)
        if node.type is not None:
            if node.ident in env:
                raise RuntimeError(f"Error: {node.ident} already initialized")
            env[node.ident] = value
        else:
            if node.ident not in env:
                raise RuntimeError(f"Error: Cannot reassign undeclared variable {node.ident}")
            env[node.ident] = value
        return value
    
    elif isinstance(node, Type_Node):
        return node.type

    elif isinstance(node, BinOps_Node):
        left = eval_ast(node.left, env, in_loop=in_loop)
        right = eval_ast(node.right, env, in_loop=in_loop)
        if node.ops == "+":
            return left + right
        elif node.ops == "-":
            return left - right
        elif node.ops == "*":
            return left * right
        elif node.ops == "/":
            if right == 0:
                raise ZeroDivisionError("Error: Division by zero not allowed")
            return left / right   
        elif node.ops == "%":
            if right == 0:
                raise ZeroDivisionError("Error: Division by zero not allowed")
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
        elif node.ops in ["&", "and"]:
            return left and right
        elif node.ops in ["|", "or"]:
            return left or right 
    
    elif isinstance(node, Variable_Node):
        if node.ident not in env:
            raise RuntimeError(f"Error: Variable {node.ident} not initialized")
        return env[node.ident]
        
    elif isinstance(node, SingleOps_Node):
        right = eval_ast(node.right, env, in_loop=in_loop)
        if node.ops == "!":
            return not right
        elif node.ops == "-":
            return -right 
        
    elif isinstance(node, Disp_Node):
        expression = eval_ast(node.expr, env, in_loop=in_loop)
        print(expression)
        return None
        
    elif isinstance(node, Entry_Node):
        expression = eval_ast(node.expr, env, in_loop=in_loop) if node.expr else ""
        return input(expression)
       
    elif isinstance(node, If_Else_Node):
        condition = eval_ast(node.condition, env, in_loop=in_loop)
        if condition:
            result = None
            for stmt in node.if_block:
                result = eval_ast(stmt, env, in_loop=in_loop)
            return result
        else:
            if node.else_block:
                result = None
                for stmt in node.else_block:
                    result = eval_ast(stmt, env, in_loop=in_loop)
                return result 
            return None
    
    elif isinstance(node, While_Node):
        result = None
        while True:
            condition = eval_ast(node.condition, env, in_loop=in_loop)
            if not condition:
                break
            try:
                for stmt in node.while_block:
                    result = eval_ast(stmt, env, in_loop=True)
            except Continue_Exception:
                continue
            except Break_Exception:
                break
        return result
        
    elif isinstance(node, Break_Node):
        if not in_loop:
            raise RuntimeError("Error: 'Break' outside loop")
        raise Break_Exception()
    
    elif isinstance(node, Continue_Node):
        if not in_loop:
            raise RuntimeError("Error: 'Continue' outside loop")
        raise Continue_Exception()

    elif isinstance(node, Return_Node):
        if node.expr:
            value = eval_ast(node.expr, env, in_loop=in_loop)
            raise Return_Exception(value)
        else:
            raise Return_Exception(None)
        
    elif isinstance(node, Function_Node):
        if node.ident in env:
            raise RuntimeError(f"Error: Function {node.ident} already defined")
        env[node.ident] = node
        return None 
    
    elif isinstance(node, Call_Node):
        if node.ident not in env:
            raise RuntimeError(f"Error: Function {node.ident} not defined")
        func = env[node.ident]
        if not isinstance(func, Function_Node):
            raise RuntimeError(f"Error: {node.ident} is not a function")
        
        args = node.parameter if node.parameter else []
        eval_args = [eval_ast(arg, env, in_loop=in_loop) for arg in args]
        params = func.parameter if func.parameter else []
        if len(eval_args) != len(params):
            raise RuntimeError(f"Error: Function {node.ident} expected {len(params)} arguments, got {len(eval_args)}")
        
        local_env = dict(env)
        for param, arg_val in zip(params, eval_args):
            param_name = param.ident if hasattr(param, 'ident') else param
            local_env[param_name] = arg_val
                  
        result = None
        try:
            for stmt in func.body:
                result = eval_ast(stmt, local_env, in_loop=False)
        except Return_Exception as ret:
            return ret.value
        
        return result
        
    elif isinstance(node, For_Node):
        local_env = dict(env)
        if node.init:
            eval_ast(node.init, local_env, in_loop=False)
            
        result = None
        while True:
            condition_val = eval_ast(node.condition, local_env, in_loop=in_loop)
            if not condition_val:
                break
            try:
                for stmt in node.for_block:
                    result = eval_ast(stmt, local_env, in_loop=True)
            except Continue_Exception:
                pass
            except Break_Exception:
                break
            if node.update:
                eval_ast(node.update, local_env, in_loop=False)
        return result

if __name__ == "__main__":
    from lexicals import lexer
    from parse import parser
    from semantics import SymbolTable, check
    
    test_code = """
    let x: int = 10;
    let y: int = 20;
    fn add: int [a: int, b: int]: {
        return a + b;
    }
    disp(add(x, y));
    """
    ast = parser.parse(test_code, lexer=lexer)
    symtab = SymbolTable()
    for stmt in ast:
        check(stmt, symtab)
    env = {}
    for stmt in ast:
        eval_ast(stmt, env)