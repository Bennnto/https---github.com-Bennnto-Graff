from parse import (Assign_Node, Int_Node, Type_Node, BinOps_Node, Str_Node, 
                   SingleOps_Node, Variable_Node, Bool_Node, Disp_Node, Entry_Node,
                   If_Else_Node, Break_Exception, Continue_Exception, While_Node,
                   Break_Node, Continue_Node, Return_Exception, Return_Node, Void_Node, Function_Node, 
                   Call_Node, For_Node, Float_Node, Array_Node, Index_Node, Index_Assign_Node, Method_Call_Node,
                   Array_Type_Node, Hash_Node, Hash_Type_Node, Throw_Node, Try_Ok_Node,
                   Assert_Node, Assert_Eq_Node, Attempt_Node, Lambda_Node, Box_Node, Move_Node, Ref_Node, Deref_Node, Deref_Assign_Node,
                   Fstr_Node)
from environment import Environment
import re
from lexicals import lexer
from parse import parser

class HeapPointer:
    def __init__(self, address):
        self.address = address

class RefPointer:
    def __init__(self, var_name, is_mutable=False):
        self.var_name = var_name
        self.is_mutable = is_mutable

heap_store = {}
heap_next_addr = 0x1000

class VelnException(Exception):
    def __init__(self, message):
        self.message = str(message)

class RuntimeHash:
    def __init__(self, pairs=None):
        self.data = {}
        if pairs:
            for k, v in pairs:
                self.data[k] = v

    def get(self, key):
        if key not in self.data:
            raise RuntimeError(f"Error : key {key} not found in hash")
        return self.data[key]
    
    def set(self, key, value):
        self.data[key] = value

    def len(self):
        return len(self.data)

    def keys(self):
        return RuntimeArray(list(self.data.keys()))

    def values(self):
        return RuntimeArray(list(self.data.values()))

    def contains(self, key):
        return key in self.data

    def remove(self, key):
        if key not in self.data:
            raise RuntimeError(f"Error : key {key} not found in hash")
        del self.data[key]
        return self.data

    def clear(self):
        self.data.clear()

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
        block_env = Environment(parent=env)
        if condition:
            result = None
            for stmt in node.if_block:
                result = eval_ast(stmt, block_env, in_loop=in_loop)
            return result
        else:
            if node.else_block:
                result = None
                for stmt in node.else_block:
                    result = eval_ast(stmt, block_env, in_loop=in_loop)
                return result 
            return None
    
    elif isinstance(node, While_Node):
        result = None
        while True:
            condition = eval_ast(node.condition, env, in_loop=in_loop)
            if not condition:
                break
            block_env = Environment(parent=env)
            try:
                for stmt in node.while_block:
                    result = eval_ast(stmt, block_env, in_loop=True)
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

        if callable(func):
            eval_args = [eval_ast(arg, env, in_loop) for arg in (node.parameter or [])]
            return func(*eval_args)

        if not isinstance(func, Function_Node):
            raise RuntimeError(f"Error: {node.ident} is not a function")
        
        args = node.parameter if node.parameter else []
        eval_args = [eval_ast(arg, env, in_loop=in_loop) for arg in args]
        params = func.parameter if func.parameter else []
        if len(eval_args) != len(params):
            raise RuntimeError(f"Error: Function {node.ident} expected {len(params)} arguments, got {len(eval_args)}")
        
        func_env = Environment(parent=env)
        for param, arg_val in zip(params, eval_args):
            param_name = param.ident if hasattr(param, 'ident') else param
            func_env.set(param_name, arg_val)
                  
        result = None
        try:
            for stmt in func.body:
                result = eval_ast(stmt, func_env, in_loop=False)
        except Return_Exception as ret:
            return ret.value
        
        return result
        
    elif isinstance(node, For_Node):
        for_env = Environment(parent=env)
        if node.init:
            eval_ast(node.init, for_env, in_loop=False)
            
        result = None
        while True:
            condition_val = eval_ast(node.condition, for_env, in_loop=in_loop)
            if not condition_val:
                break
            block_env = Environment(parent=for_env)
            try:
                for stmt in node.for_block:
                    result = eval_ast(stmt, block_env, in_loop=True)
            except Continue_Exception:
                pass
            except Break_Exception:
                break
            if node.update:
                eval_ast(node.update, for_env, in_loop=False)
        return result
    
    elif isinstance(node, Array_Node):                                                                                                          
        evaluated_elements = [eval_ast(elem, env, in_loop) for elem in node.elements]                                                          
        return RuntimeArray(evaluated_elements)                                                                                                
                                                                                                                                               
    elif isinstance(node, Index_Node):                                                                                                         
        target = eval_ast(node.target, env, in_loop)                                                                                           
        index = eval_ast(node.index, env, in_loop)                                                                                             
        if isinstance(target, RuntimeArray):                                                                                                                                                                             
            return target.get(index)                                                                                                               
        if isinstance(target, RuntimeHash):
            return target.get(index)
        raise RuntimeError("Error: Target is not an array or hash")   

    elif isinstance(node, Index_Assign_Node):                                                                                                  
        target = eval_ast(node.target, env, in_loop)                                                                                           
        index = eval_ast(node.index, env, in_loop)                                                                                             
        value = eval_ast(node.value, env, in_loop)                                                                                             
        if isinstance(target, RuntimeArray):                                                                                                                                                                                 
            target.set(index, value)
            return value
        if isinstance(target, RuntimeHash):
            target.set(index, value)
            return value
        raise RuntimeError("Error: Index assignment target is not an array or hash") 
  
    elif isinstance(node, Method_Call_Node):
        target_obj = eval_ast(node.target, env, in_loop)
        eval_args = [eval_ast(arg, env, in_loop) if not isinstance(arg, list) else [eval_ast(x, env, in_loop) for x in arg] for arg in (node.args if node.args else [])]
  
        if not hasattr(target_obj, node.method):
            raise RuntimeError(f"Error: Object has no method '{node.method}'")
  
        method = getattr(target_obj, node.method)
        return method(*eval_args)

    elif isinstance(node, Hash_Node):
        pairs = [(eval_ast(key, env, in_loop), eval_ast(val, env, in_loop)) for key, val in node.elements]
        return RuntimeHash(pairs)

    elif isinstance(node, Throw_Node):
        val = eval_ast(node.expr, env, in_loop)
        raise VelnException(str(val))

    elif isinstance(node, Try_Ok_Node):
        try_env = Environment(parent=env)
        is_ok = True
        err_msg = ""
        result = None
        try:
            if isinstance(node.try_block, list):
                for stmt in node.try_block:
                    result = eval_ast(stmt, try_env, in_loop)
            else:
                result = eval_ast(node.try_block, try_env, in_loop)
        except (VelnException, RuntimeError, ZeroDivisionError, TypeError, KeyError) as ex:
            is_ok = False
            err_msg = ex.message if isinstance(ex, VelnException) else str(ex)

        ok_env = Environment(parent=env)
        ok_env.set(node.is_ok_ident, is_ok)
        ok_env.set(node.err_ident, err_msg)

        if isinstance(node.ok_block, list):
            for stmt in node.ok_block:
                result = eval_ast(stmt, ok_env, in_loop)
        else:
            result = eval_ast(node.ok_block, ok_env, in_loop)

        return result

    elif isinstance(node, Assert_Node):
        cond = eval_ast(node.condition, env, in_loop)
        if not cond:
            msg = eval_ast(node.message, env, in_loop) if node.message else "Assertion Failed"
            raise VelnException(f"Assertion Error: {msg}")
        return None

    elif isinstance(node, Assert_Eq_Node):
        actual = eval_ast(node.actual, env, in_loop)
        expected = eval_ast(node.expected, env, in_loop)
        if actual != expected:
            raise VelnException(f"Assertion Error: Expected {expected}, got {actual}")
        return None

    elif isinstance(node, Attempt_Node):
        attempt_env = Environment(parent=env)
        retry_count = eval_ast(node.retry, env, in_loop)
        i = 0
        result = None
        while i < retry_count :
            try:
                if isinstance(node.attempt_block, list):
                    for stmt in node.attempt_block:
                        result=eval_ast(stmt, attempt_env, in_loop)
                else:
                    result=eval_ast(node.attempt_block, attempt_env, in_loop)
                for k, v in attempt_env.bindings.items():
                    env.set(k, v)
                return result
            except Return_Exception:
                for k, v in attempt_env.bindings.items():
                    env.set(k, v)
                return result
            except (VelnException, RuntimeError, ZeroDivisionError, TypeError, KeyError) as ex:
                last_ex = ex
                i += 1
        if node.fallback_block is not None :
            fb_env = Environment(parent=env)   
            if isinstance(node.fallback_block, list) :
                for stmt in node.fallback_block:
                    result = eval_ast(stmt, fb_env, in_loop)
                return result
            else:
                result = eval_ast(node.fallback_block, fb_env, in_loop)
            
            for k, v in fb_env.bindings.items():
                env.set(k, v)
            return result
        elif last_ex:
            raise last_ex
        return None
         
    elif isinstance(node, Lambda_Node):
        capture_env = env
        def lambda_func(*args):
            local_env = Environment(parent=capture_env)
            params = node.params if node.params else []
            for i, param in enumerate(params):
                param_name = param.ident if hasattr(param, 'ident') else param

                local_env.set(param_name, args[i])
            return eval_ast(node.body, local_env, in_loop)
        return lambda_func      

    elif isinstance(node, Box_Node):
        val = eval_ast(node.expr, env, in_loop)
        global heap_next_addr
        addr = heap_next_addr
        heap_store[addr] = val
        heap_next_addr += 4
        return HeapPointer(addr)

    elif isinstance(node, Move_Node):
        val = env.get(node.var_name)
        if val == "MOVED":
            raise VelnException(f"UserAfterMoveError: Cannot use moved variable '{node.var_name}'")
        env.set(node.var_name, "MOVED")
        return val

    elif isinstance(node, Ref_Node):
        return RefPointer(node.var_name, is_mutable=node.is_mutable)

    elif isinstance(node, Deref_Node):
        target = eval_ast(node.expr, env, in_loop)
        if isinstance(target, RefPointer):
            val = env.get(target.var_name)
            if val == "MOVED":
                raise VelnException(f"UseAfterMoveError: Cannot dereference moved variable '{target.var_name}'")
            return val
        elif isinstance(target, HeapPointer):
            return heap_store.get(target.address)
        return target

    elif isinstance(node, Deref_Assign_Node):
        target_ref = eval_ast(node.target, env, in_loop)
        val = eval_ast(node.value, env, in_loop)
        if isinstance(target_ref, RefPointer):
            if not target_ref.is_mutable:
                raise VelnException(f"Error : Cannot mutate through immutable reference to '{target_ref.var_name}'")
            env.set(target_ref.var_name, val)
        elif isinstance(target_ref, HeapPointer):
            heap_store[target_ref.address] = val
        return val

    elif isinstance(node, Fstr_Node):
        raw = node.raw
        result = ""
        last_end = 0 

        for match in re.finditer(r'\{([^}]+)\}', raw):
            result += raw[last_end:match.start()]      
            expr_text = match.group(1).strip()
            expr_ast = parser.parse(expr_text, lexer=lexer)

            if isinstance(expr_ast, list) and len(expr_ast) > 0 :
                val = eval_ast(expr_ast[0], env, in_loop)
            else:
                val = eval_ast(expr_ast, env, in_loop)
            result += str(val)
            last_end = match.end()
        result += raw[last_end:]
        return result 
        

                        
