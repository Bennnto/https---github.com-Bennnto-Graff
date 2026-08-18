import functools
from parse import (Assign_Node, Int_Node, Type_Node, BinOps_Node, Str_Node, 
                   SingleOps_Node, Variable_Node, Bool_Node, Disp_Node, Entry_Node,
                   Break_Exception, Continue_Exception, While_Node, Break_Node, Continue_Node, Return_Exception, Return_Node, Void_Node, Function_Node, 
                   Call_Node, For_Node, Float_Node, Array_Node, Index_Node, Index_Assign_Node, Method_Call_Node,
                   Array_Type_Node, Hash_Node, Hash_Type_Node, Throw_Node, Try_Ok_Node,
                   Assert_Node, Assert_Eq_Node, Attempt_Node, Lambda_Node, Box_Node, Move_Node, Ref_Node, Deref_Node, Deref_Assign_Node,
                   Fstr_Node, Case_Node, Match_Node, Ternary_Node, Timeline_Rollback_Node, Timeline_Index_Node, Timeline_Decl, Enum_Node
                   , Fix_Node, Struct_Decl_Node, Struct_Literal_Node, Field_Access_Node, Impl_Node, Bind_Node, Range_Node, Pub_Node, For_Range_Node, Drop_Node,
                   Async_Node, Await_Node, Gaff_Node)
from environment import Environment
import re
from lexicals import lexer
from parse import parser
import threading



class HeapPointer:
    def __init__(self, address):
        self.address = address

class RefPointer:
    def __init__(self, var_name, is_mutable=False):
        self.var_name = var_name
        self.is_mutable = is_mutable

heap_store = {}
heap_next_addr = 0x1000

class GaffException(Exception):
    def __init__(self, message):
        self.message = str(message)

VelnException = GaffException

class RuntimeStruct:
    def __init__(self, name, fields):
        self.name = name
        self.fields = fields

    def __repr__(self):
        return f"{self.name}{self.fields}"

class RuntimeEnum:
    def __init__(self, name, members):
        self.name = name
        self.members = members
        
    def get(self, member_name):
        if member_name not in self.members :
            raise RuntimeError(f"Error : Enum {self.name} has no member {member_name}")
        return self.members[member_name]
    
    def contains(self, member_name):
        return member_name in self.members
    
    def keys(self):
        return RuntimeArray(list(self.members.keys()))
    
    def values(self):
        return RuntimeArray(list(self.members.values())) 
    
    def name_of(self, val):
        for name, value in self.members.items():
            if value == val:
                return name
        raise RuntimeError(f"Error : Value {val} not found in Enum {self.name}")
    
    def len(self):
        return len(self.members)
    
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
        if isinstance(index, slice):
            return RuntimeArray(self.elements[index])
        if isinstance(index, range):
            return RuntimeArray(self.elements[index.start:index.stop])
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


def set_var(env, name, val):
    if hasattr(env, 'set'):
        env.set(name, val)
    elif hasattr(env, 'bindings'):
        env.bindings[name] = val
    elif isinstance(env, dict):
        env[name] = val

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

    elif isinstance(node, Range_Node):
        start = eval_ast(node.start, env, in_loop) if node.start is not None else 0
        stop = eval_ast(node.stop, env, in_loop) if node.stop is not None else None
        step = eval_ast(node.step, env, in_loop) if node.step is not None else 1
        return slice(start, stop, step)
    
    elif isinstance(node, Assign_Node):
        if isinstance(env, Environment) and env.is_immutable(node.ident):
            raise RuntimeError(f"Error : Cannot reassign fix variable {node.ident}")
        value = eval_ast(node.value, env, in_loop=in_loop)
        if isinstance(value, RuntimeArray) and isinstance(node.type, Array_Type_Node):
            if node.type.length is not None:
                if len(value.elements) != node.type.length:
                    raise RuntimeError(f"Error: Fixed array expected {node.type.length} elements, got {len(value.elements)}")
                value.max_len = node.type.length
        
        # If existing value is a timeline (plain Python list), append to history
        existing = env.get(node.ident, None) if isinstance(env, dict) else env.get(node.ident, None)
        if isinstance(existing, list) and not isinstance(existing, RuntimeArray):
            existing.append(value)
        else:
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
        elif node.ops == "**":
            return left ** right
        elif node.ops == "/":
            if right == 0:
                raise ZeroDivisionError("Error: Division by zero not allowed")
            return left / right   
        elif node.ops == "%":
            if right == 0:
                raise ZeroDivisionError("Error: Division by zero not allowed")
            return left % right
        elif node.ops == "<<":
            return left << right
        elif node.ops == ">>":
            return left >> right
        elif node.ops == "^":
            return left ^ right
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
            return left & right if isinstance(left, int) and isinstance(right, int) else (left and right)
        elif node.ops in ["|", "or"]:
            return left | right if isinstance(left, int) and isinstance(right, int) else (left or right)
    
    elif isinstance(node, Variable_Node):
        if node.ident not in env:
            raise RuntimeError(f"Error: Variable {node.ident} not initialized")
        return env[node.ident]
        
    elif isinstance(node, SingleOps_Node):
        right = eval_ast(node.right, env, in_loop=in_loop)
        if node.ops == "~":
            return ~right
        elif node.ops == "!":
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
        if isinstance(node.ident, str):
            func = env.get(node.ident)
        else:
            func = eval_ast(node.ident, env, in_loop=in_loop)
            
        args = node.parameter if node.parameter else []
        eval_args = [eval_ast(arg, env, in_loop=in_loop) for arg in args]
        
        if callable(func):
            return func(*eval_args)
            
        if not isinstance(func, Function_Node) and not isinstance(func, dict):
            raise RuntimeError(f"Error: {node.ident} is not callable")
        
        params = func.parameter if hasattr(func, 'parameter') else func.get('params', [])
        func_env = Environment(parent=env)
        for i, param in enumerate(params):
            param_name = param.ident if hasattr(param, 'ident') else param
            if i < len(eval_args):
                func_env.set(param_name, eval_args[i])
            elif hasattr(param, 'value') and param.value is not None:
                default_val = eval_ast(param.value, env, in_loop=in_loop)
                func_env.set(param_name, default_val)
            else:
                raise RuntimeError(f"Error: Function missing argument for '{param_name}'")
                  
        result = None
        body = func.body if hasattr(func, 'body') else func.get('body', [])
        try:
            for stmt in body:
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

    elif isinstance(node, For_Range_Node):
        r = node.range
        start = eval_ast(r.start, env, in_loop) if getattr(r, 'start', None) is not None else 0
        stop = eval_ast(r.stop, env, in_loop) if getattr(r, 'stop', None) is not None else 0
        step = eval_ast(r.step, env, in_loop) if getattr(r, 'step', None) is not None else 1
        
        loop_env = Environment(parent=env)
        res = None
        for i in range(start, stop, step):
            set_var(loop_env, node.ident, i)
            set_var(env, node.ident, i)
            try:
                if isinstance(node.for_block, list):
                    for stmt in node.for_block:
                        res = eval_ast(stmt, loop_env, in_loop=True)
                else:
                    res = eval_ast(node.for_block, loop_env, in_loop=True)
                for k, v in loop_env.bindings.items():
                    set_var(env, k, v)
            except Break_Exception:
                break
            except Continue_Exception:
                continue
        return res
    
    elif isinstance(node, Array_Node):                                                                                                          
        evaluated_elements = [eval_ast(elem, env, in_loop) for elem in node.elements]                                                          
        return RuntimeArray(evaluated_elements)                                                                                                
                                                                                                                                               
    elif isinstance(node, Index_Node):
        target = eval_ast(node.target, env, in_loop)
        index = eval_ast(node.index, env, in_loop)
        if isinstance(target, str):
            return target[index]
        if isinstance(target, RuntimeArray):
            return target.get(index)                                                                                                               
        if isinstance(target, RuntimeHash):
            return target.get(index)
        if isinstance(target, RuntimeEnum):
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
    elif isinstance(node, Method_Call_Node):
        target_obj = eval_ast(node.target, env, in_loop)
        eval_args = [eval_ast(arg, env, in_loop) if not isinstance(arg, list) else [eval_ast(x, env, in_loop) for x in arg] for arg in (node.args if node.args else [])]
        if isinstance(target_obj, Environment):
            if target_obj.contains(node.method):
                fn = target_obj.get(node.method)
                if isinstance(fn, Function_Node) or isinstance(fn, dict):
                    fn_env = Environment(parent=target_obj)
                    params = fn.parameter if hasattr(fn, 'parameter') else fn.get('params', [])
                    for i, param in enumerate(params):
                        pname = param.ident if hasattr(param, 'ident') else param
                        if i < len(eval_args):
                            fn_env.set(pname, eval_args[i])
                    try:
                        body = fn.body if hasattr(fn, 'body') else fn.get('body', [])
                        res = None
                        for stmt in body:
                            res = eval_ast(stmt, fn_env, in_loop=False)
                        return res
                    except Return_Exception as ret:
                        return ret.value
                elif callable(fn):
                    return fn(*eval_args)
            raise RuntimeError(f"Error : Module has no function '{node.method}'")
        
        if isinstance(target_obj, RuntimeStruct):
            struct_methods = env.get(f"__struct_methods_{target_obj.name}__", None)
            if struct_methods and node.method in struct_methods:
                method_node = struct_methods[node.method]
                method_env = Environment(parent=env)
                method_env.set("self", target_obj)
                params = method_node.parameter if method_node.parameter else []
                arg_idx = 0
                for p in params:
                    if p.ident == "self":
                        continue
                    if arg_idx < len(eval_args):
                        method_env.set(p.ident, eval_args[arg_idx])
                        arg_idx += 1
                try:
                    for stmt in method_node.body:
                        eval_ast(stmt, method_env, in_loop)
                    return None
                except Return_Exception as ret:
                    return ret.value
            raise RuntimeError(f"Error : Struct '{target_obj.name}' has no method '{node.method}'")

        # Timeline method: x.history() → returns the full version list
        if isinstance(target_obj, list) and node.method == 'history':
            return list(target_obj)
            
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
                    set_var(env, k, v)
                return result
            except Return_Exception:
                for k, v in attempt_env.bindings.items():
                    set_var(env, k, v)
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
            fmt_spec = None
            if ':' in expr_text and not expr_text.startswith('::'):
                expr_text, fmt_spec = expr_text.split(':', 1)
            expr_ast = parser.parse(expr_text, lexer=lexer)

            if isinstance(expr_ast, list) and len(expr_ast) > 0 :
                val = eval_ast(expr_ast[0], env, in_loop)
            else:
                val = eval_ast(expr_ast, env, in_loop)
            if fmt_spec:
                result += format(val, fmt_spec)
            else:
                result += str(val)
            last_end = match.end()
        result += raw[last_end:]
        return result 


    elif isinstance(node, Match_Node):
        target_val = eval_ast(node.target, env, in_loop=in_loop)
        for case in node.cases :
            is_wildcard = isinstance(case.pattern, Variable_Node) and case.pattern.ident == "_"
            if is_wildcard or eval_ast(case.pattern, env, in_loop=in_loop) == target_val :
                block_env = Environment(parent=env)
                result = None
                for stmt in case.body :
                    result = eval_ast(stmt, block_env, in_loop=in_loop)
                return result 
        return None

    elif isinstance(node, Ternary_Node):
        condition_val = eval_ast(node.condition, env, in_loop)
        func_env = Environment(parent=env)
        result= None
        if condition_val:
            if node.true_block:
                if isinstance(node.true_block, list):
                    for stmt in node.true_block:
                        result = eval_ast(stmt, func_env, in_loop=in_loop)
                    return result
                else:
                    return eval_ast(node.true_block, func_env, in_loop=in_loop)
        else:
            if node.false_block:
                if isinstance(node.false_block, list):
                    for stmt in node.false_block:
                        result = eval_ast(stmt, func_env, in_loop=in_loop)
                    return result
                else:
                    return eval_ast(node.false_block, func_env, in_loop=in_loop)
        return None

    elif isinstance(node, Timeline_Decl):
        ident = node.ident
        value = eval_ast(node.value, env, in_loop)
        env[ident] = [value]
        return value 

    elif isinstance(node, Timeline_Index_Node):
        history = eval_ast(node.target, env, in_loop)
        index = eval_ast(node.index, env, in_loop)

        if not isinstance(history, list):
            raise VelnException(f"Error : Timeline Variable expected 'list'")

        if index >= len(history):
            raise VelnException(f"Error : Timeline index {index} out of range has {len(history)} versions")

        return history[index]

    elif isinstance(node, Timeline_Rollback_Node):
        history = env[node.ident]

        if not isinstance(history, list):
            raise VelnException(f"Error : '{node.ident}' is not a timeline variable")

        if node.index is not None:
            idx = eval_ast(node.index, env, in_loop)
            if idx >= len(history):
                raise VelnException(f"Error : Timeline index {idx} out of range has {len(history)} versions")
            env[node.ident] = history[:idx + 1]
        else:
            if len(history) > 1:
                env[node.ident] = history[:-1]
        return env[node.ident][-1]
    
    elif isinstance(node, Enum_Node):
        eval_members = {}
        current_auto_val = 0
        for item in node.members:
            if isinstance(item, tuple):
                member_name, expr = item
            else:
                member_name = getattr(item, 'naame', str(item))
                expr = getattr(item, 'value', None)
            
            if expr is not None :
                val = eval_ast(expr, env, in_loop=in_loop)
                eval_members[member_name] = val
                if isinstance(val, int):
                    current_auto_val = val + 1
            else:
                eval_members[member_name] = current_auto_val
                current_auto_val += 1
                    
        enum_obj = RuntimeEnum(node.name, eval_members)
        env.set(node.name, enum_obj)
        return enum_obj
    
    elif isinstance(node, Fix_Node):
        ident = node.ident if isinstance(node.ident, str) else eval_ast(node.ident, env, in_loop)
        value = eval_ast(node.value, env, in_loop)
        if node.ident in env :
            raise RuntimeError(f"Error : Fix variable {node.ident} already declared")
        env[ident] = value
        if isinstance(env, Environment):
            env.mark_immutable(ident)
        return value

    elif isinstance(node, Struct_Decl_Node):
        return None

    elif isinstance(node, Struct_Literal_Node):
        fields = {
            fname: eval_ast(fexpr, env, in_loop)
            for fname, fexpr in node.field_values.items()
        }
        return RuntimeStruct(node.name, fields)

    elif isinstance(node, Field_Access_Node):
        target_obj = eval_ast(node.target, env, in_loop)
        if isinstance(target_obj, RuntimeStruct):
            if node.field in target_obj.fields:
                return target_obj.fields[node.field]
            raise RuntimeError(f"Error : Field '{node.field}' not found in struct {target_obj.name}")
        if isinstance(target_obj, RuntimeEnum):
            return target_obj.get(node.field)
        if isinstance(target_obj, Environment):
            if target_obj.contains(node.field):
                return target_obj.get(node.field)
            raise RuntimeError(f"Error : Module has no attribute '{node.field}'")
        if isinstance(target_obj, dict):
            return target_obj.get(node.field)
        if hasattr(target_obj, node.field):
            return getattr(target_obj, node.field)
        raise RuntimeError(f"Error : Target is not a struct or enum, got {type(target_obj).__name__}")

    elif isinstance(node, Bind_Node):
        path_str = node.path.value if hasattr(node.path, 'value') else str(node.path)
        alias_name = node.alias if isinstance(node.alias, str) else (node.alias.ident if hasattr(node.alias, 'ident') else str(node.alias))
        import os
        if os.path.exists(path_str):
            with open(path_str, 'r', encoding='utf-8') as f:
                code = f.read()
            mod_ast = parser.parse(code, lexer=lexer)
            mod_env = Environment()
            if mod_ast:
                for stmt in mod_ast:
                    eval_ast(stmt, mod_env)
            if node.alias == "*":
                for k, v in mod_env.bindings.items():
                    set_var(env, k, v)
            elif isinstance(node.alias, (list, tuple)):
                for item in node.alias:
                    sym_name = item.ident if hasattr(item, 'ident') else str(item)
                    if sym_name in mod_env.bindings:
                        set_var(env, sym_name, mod_env.bindings[sym_name])
            else:
                if alias_name in mod_env.bindings:
                    set_var(env, alias_name, mod_env.bindings[alias_name])
                else:
                    set_var(env, alias_name, mod_env)
            return mod_env
        else:
            import std_lib
            mod_obj = std_lib.load_module(path_str)
            if isinstance(node.alias, (list, tuple)):
                for item in node.alias:
                    sym_name = item.ident if hasattr(item, 'ident') else str(item)
                    if isinstance(mod_obj, dict) and sym_name in mod_obj:
                        set_var(env, sym_name, mod_obj[sym_name])
                    elif hasattr(mod_obj, sym_name):
                        set_var(env, sym_name, getattr(mod_obj, sym_name))
                return mod_obj
            else:
                set_var(env, alias_name, mod_obj)
                return mod_obj

    elif isinstance(node, Impl_Node):
        key = f"__struct_methods_{node.struct_name}__"
        methods_dict = env.get(key, None) if env.contains(key) else {}
        if methods_dict is None:
            methods_dict = {}
        for method in node.methods:
            methods_dict[method.ident] = method
        env.set(key, methods_dict)
        return None

    elif isinstance(node, Pub_Node):
        return eval_ast(node.node, env, in_loop=in_loop)

    elif isinstance(node, Drop_Node):
        if env.contains(node.target):
            val = env.get(node.target, None)
            if isinstance(val, HeapPointer) and val.address in heap_store:
                del heap_store[val.address]
            if node.target in env.bindings:
                del env.bindings[node.target]
        return None

    elif isinstance(node, Async_Node):
        fn = node.func
        fn.is_async = True
        env.set(fn.ident, fn)   # Environment uses .set(), not dict brackets
        return None

    elif isinstance(node, Await_Node):
        result_box = eval_ast(node.expr, env, in_loop=in_loop)
        if isinstance(result_box, dict) and '__thread__' in result_box:
            result_box['__thread__'].join()
            return result_box['__result__']
        return result_box

    elif isinstance(node, Gaff_Node):
        def constraint_fn(new_val):
            hook_env = Environment(parent=env)
            # Bind the variable to the new value within the constraint check
            hook_env.bindings[node.ident] = new_val
            
            result = None
            if isinstance(node.gaff_block, list):
                for stmt in node.gaff_block:
                    result = eval_ast(stmt, hook_env, in_loop=in_loop)
            else:
                result = eval_ast(node.gaff_block, hook_env, in_loop=in_loop)
                
            if result is False:
                raise RuntimeError(f"Error : Constraint on '{node.ident}' violated.")
                
        env.add_hook(node.ident, constraint_fn)
        
        # Check immediately for the current value if it exists
        if env.contains(node.ident):
            constraint_fn(env.get(node.ident))
        return None