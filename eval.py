from parse import (Assign_Node, Int_Node, Type_Node, BinOps_Node, Str_Node, 
                   SingleOps_Node, Variable_Node, Bool_Node, Disp_Node, Entry_Node,
                   If_Else_Node, Break_Exception, Continue_Exception, While_Node,
                   Break_Node, Continue_Node, Return_Exception, Return_Node, Void_Node, Function_Node, 
                   Call_Node, For_Node, Float_Node, Array_Node, Index_Node, Index_Assign_Node, Method_Call_Node,
                   Array_Type_Node)

class RuntimeArray:
    def __init__(self, elements=None, max_len=None):
        self.elements = list(elements) if elements is not None else []
        self.max_len = max_len
        
    def push(self, value):
        if self.max_len is not None:
            raise RuntimeError(f"Error: Cannot push to fixed-size array of size {self.max_len}")
        self.elements.append(value)
        return len(self.elements)
    
    def pop(self):
        if self.max_len is not None:
            raise RuntimeError(f"Error: Cannot pop from fixed-size array of size {self.max_len}")
        if not self.elements:
            raise RuntimeError("Error : Cannot pop from empty array")
        return self.elements.pop()
    
    def len(self):
        return len(self.elements)
    
    def length(self):
        return len(self.elements)

    def get(self, index):
        if not isinstance(index, int):
            raise TypeError("Error : Index must be an integer")
        if index < 0 or index >= len(self.elements):
            raise IndexError("Error : Array index out of bounds")
        return self.elements[index]
    
    def set(self, index, value):                                                                                                           
        if not isinstance(index, int):                                                                                                     
            raise TypeError("Error: Index must be an integer")                                                                             
        if index < 0 or index >= len(self.elements):                                                                                       
            raise IndexError("Error: Array index out of bounds")                                                                           
        self.elements[index] = value                                                                                                       
                                                                                                                                               
    def __repr__(self):                                                                                                                    
        return str(self.elements)   
    
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
        if isinstance(value, RuntimeArray) and isinstance(node.type, Array_Type_Node):
            if node.type.length is not None:
                if len(value.elements) != node.type.length:
                    raise RuntimeError(f"Error: Fixed array expected {node.type.length} elements, got {len(value.elements)}")
                value.max_len = node.type.length
        
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
    
    elif isinstance(node, Array_Node):                                                                                                          
        evaluated_elements = [eval_ast(elem, env, in_loop) for elem in node.elements]                                                          
        return RuntimeArray(evaluated_elements)                                                                                                
                                                                                                                                               
    elif isinstance(node, Index_Node):                                                                                                         
        target = eval_ast(node.target, env, in_loop)                                                                                           
        index = eval_ast(node.index, env, in_loop)                                                                                             
        if not isinstance(target, RuntimeArray):                                                                                               
            raise RuntimeError("Error: Target is not an array")                                                                                
        return target.get(index)                                                                                                               
                                                                                                                                               
    elif isinstance(node, Index_Assign_Node):                                                                                                  
        target = eval_ast(node.target, env, in_loop)                                                                                           
        index = eval_ast(node.index, env, in_loop)                                                                                             
        value = eval_ast(node.value, env, in_loop)                                                                                             
        if not isinstance(target, RuntimeArray):                                                                                               
            raise RuntimeError("Error: Target is not an array")                                                                                
        target.set(index, value)
        return value
  
    elif isinstance(node, Method_Call_Node):
        target_obj = eval_ast(node.target, env, in_loop)
        eval_args = [eval_ast(arg, env, in_loop) if not isinstance(arg, list) else [eval_ast(x, env, in_loop) for x in arg] for arg in (node.args if node.args else [])]
  
        if not hasattr(target_obj, node.method):
            raise RuntimeError(f"Error: Object has no method '{node.method}'")
  
        method = getattr(target_obj, node.method)
        return method(*eval_args)