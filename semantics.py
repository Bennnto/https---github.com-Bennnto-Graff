from parse import (Assign_Node, Bool_Node, Int_Node, Type_Node, BinOps_Node, Str_Node, Variable_Node,
                   SingleOps_Node, Disp_Node, Entry_Node, If_Else_Node, While_Node, Return_Node, Function_Node,
                   Call_Node, For_Node, Float_Node, Param_Node, Array_Node, Index_Node, Index_Assign_Node,
                   Method_Call_Node, Array_Type_Node)

from dataclasses import dataclass
from typing import List, Any

class SemanticError(Exception):
    pass
class TypeError(Exception):
    pass

class Type_Infer:
    def __init__(self, symtab):
        self.symtab = symtab
    
    def infer_program(self, ast):
        for node in ast:
            if isinstance(node, Function_Node):
                self.infer_function_signature(node)
            
        for node in ast:
            self.infer_node(node)

    def infer_function_signature(self, node):
        params = node.parameter if node.parameter else []
        param_types = []
        for p in params:
            p_type = get_type_name(p.type) if p.type else ('int' if p.value is None else check(p.value, self.symtab))
            param_types.append(p_type)
        
        self.symtab.push_scope()
        for p, p_type in zip(params, param_types):
            self.symtab.add(p.ident, p_type)
            
        re_type = get_type_name(node.re_type) if node.re_type else self.infer_function_return_type(node)
        self.symtab.pop_scope()
        
        self.symtab.add(node.ident, FunctionSymbol(return_type=re_type, param_types=param_types))

    def infer_function_return_type(self, node):
        for stmt in node.body:
            if isinstance(stmt, Return_Node) and stmt.expr:
                return check(stmt.expr, self.symtab)
        
        return 'void'

    def infer_node(self, node):
        if isinstance(node, Assign_Node):
            val_type = check(node.value, self.symtab)
            if not self.symtab.current_scope_contains(node.ident):
                self.symtab.add(node.ident, val_type)
            return val_type
        return check(node, self.symtab)

@dataclass
class FunctionSymbol:
    return_type : Any
    param_types : List[Any]

class SymbolTable:
    def __init__(self):
        self.scopes = [{}]
        
    # Enter new block scope for if / loop / function.    
    def push_scope(self):
        self.scopes.append({})
        
    # Exit current block scope 
    def pop_scope(self):
        if len(self.scopes) <= 1:
            raise SemanticError("Error : Cannot pop global scope")    
        self.scopes.pop()
    
    # Add symbol to current scope. Raise error if already exists.
    def add(self, name, type_str):
        if name in self.scopes[-1]:
            raise SemanticError(f"Error : Variable {name} already defined in this scope")
        self.scopes[-1][name] = type_str
    
    # Lookup symbols, searching outer scopes. Raise if not found.
    def get(self, name):
        for scope in reversed(self.scopes):
            if name in scope :
                return scope[name]
        raise SemanticError(f"Error : Variable {name} not declared")
        
    # Check current scope only (no outer scope search)
    def current_scope_contains(self, name):
        return name in self.scopes[-1]

    def contains(self, name):
        try:
            self.get(name)
            return True
        except SemanticError:
            return False

def get_type_name(t):
    if isinstance(t, Type_Node):
        t = t.type
    if isinstance(t, Array_Type_Node):
        elem = get_type_name(t.elem_type)
        return f"array[{elem},{t.length}]" if t.length is not None else f"array[{elem}]"
    mapping = {
        'INT_TYPE': 'int',
        'STR_TYPE': 'str',
        'BOOL_TYPE': 'bool',
        'FLOAT_TYPE': 'float',
        'VOID_TYPE': 'void',
    }
    return mapping.get(t, t)

# Validate semantics and types with scoped symbol table.
def check(node, symtab):
    if isinstance(node, Int_Node):
        return 'int'
    if isinstance(node, Str_Node):
        return 'str'
    if isinstance(node, Bool_Node):
        return 'bool'
    if isinstance(node, Float_Node):
        return 'float'
    if isinstance(node, Type_Node):
        return get_type_name(node)
    if isinstance(node, Array_Type_Node):
        return get_type_name(node)
    
    if isinstance(node, Assign_Node):
        value_type = check(node.value, symtab)
        if not symtab.contains(node.ident):
            symtab.add(node.ident, value_type)
            return value_type

        existing_type = symtab.get(node.ident)
        if existing_type != 'any' and value_type != existing_type:
            raise TypeError(f"Error : Cannot assign {value_type} to variable {node.ident} expected {existing_type}")
        return value_type
        
    if isinstance(node, BinOps_Node):
        left_type = check(node.left, symtab)
        right_type = check(node.right, symtab)
        if node.ops in ['>', '<', '>=', '<=', '==', '!=']:
            if left_type != right_type:
                raise TypeError(f"Error : Type Error type of {left_type} not compatible with type of {right_type}")
            return 'bool'
        elif node.ops in ['&', '|']:
            if left_type != 'bool' or right_type != 'bool':
                raise TypeError(f"Error : Logical operations require boolean types")
            return 'bool'
        else:
            if left_type != right_type:
                raise TypeError(f"Error : Type Error type of {left_type} not compatible with type of {right_type}")
            if node.ops in ['+', '-', '*', '/', '%', '**'] and left_type not in ['int', 'float', 'str', 'any']:
                raise TypeError(f"Error : Cannot perform {node.ops} on {left_type}")
            return left_type
        
    if isinstance(node, Variable_Node):
        return symtab.get(node.ident)
    
    if isinstance(node, SingleOps_Node):
        right_type = check(node.right, symtab)
        if node.ops == '!' and right_type != 'bool':
            raise TypeError(f"Error : Cannot perform NOT on {right_type}")
        if node.ops == '-' and right_type not in ['int', 'float']:
            raise TypeError(f"Error : Cannot perform unary minus on {right_type}")
        return right_type 
          
    if isinstance(node, Disp_Node):
        check(node.expr, symtab)
        return None
    
    if isinstance(node, Entry_Node):
        if node.expr:
            check(node.expr, symtab)
        return 'str'
    
    if isinstance(node, If_Else_Node):
        condition_type = check(node.condition, symtab)
        if condition_type != 'bool':
            raise TypeError(f"Error : Expected boolean type for condition")
        for stmt in node.if_block:
            check(stmt, symtab)
        
        if node.else_block:
            for stmt in node.else_block:
                check(stmt, symtab)
        return None 
    
    if isinstance(node, While_Node):
        condition_type = check(node.condition, symtab)
        if condition_type != 'bool':
            raise TypeError(f"Error : Expected boolean type for condition")
        symtab.push_scope()
        for stmt in node.while_block:
            check(stmt, symtab)
        symtab.pop_scope()
        return None
    
    if isinstance(node, Return_Node):
        return check(node.expr, symtab) if node.expr else 'void'
        
    if isinstance(node, Function_Node):
        if symtab.current_scope_contains(node.ident):
            existing = symtab.get(node.ident)
            if not isinstance(existing, FunctionSymbol):
                raise SemanticError(f"Error : Symbol {node.ident} already defined in this scope")
        else:
            params = node.parameter if node.parameter else []
            param_types = [get_type_name(p.type) if p.type else 'any' for p in params]
            re_type = get_type_name(node.re_type) if node.re_type else 'any'
            symtab.add(node.ident, FunctionSymbol(return_type=re_type, param_types=param_types))
        
        params = node.parameter if node.parameter else []
        symtab.push_scope()
        for p in params:
            p_type = get_type_name(p.type) if p.type else 'any'
            if symtab.current_scope_contains(p.ident):
                raise SemanticError(f"Error : Parameter {p.ident} already defined in this scope")
            symtab.add(p.ident, p_type)
            
        for stmt in node.body :
            check(stmt, symtab)
            
        symtab.pop_scope()
        return None
    
    if isinstance(node, Call_Node):
        func_symbol = symtab.get(node.ident)
        if not isinstance(func_symbol, FunctionSymbol):
            raise TypeError(f"Error : {node.ident} is not a function")
        args = node.parameter if node.parameter else []
        if len(args) != len(func_symbol.param_types):
            raise TypeError(f"Error : Function {node.ident} expected {len(func_symbol.param_types)} arguments got {len(args)}")
        for arg, expected_type in zip(args, func_symbol.param_types):
            arg_type = check(arg, symtab)
            if arg_type != expected_type:
                raise TypeError(f"Error : Type Error type of {arg_type} not compatible with expected {expected_type}")           
        return func_symbol.return_type
    
    if isinstance(node, For_Node):
        symtab.push_scope()
        if node.init :
            check(node.init, symtab)
        condition_type = check(node.condition, symtab)
        if condition_type != 'bool':
            raise TypeError(f"Error : condition has {condition_type} type expected boolean type")
        
        if node.update:
            check(node.update, symtab)
        
        for stmt in node.for_block:
            check(stmt, symtab)
            
        symtab.pop_scope()
        return None

    if isinstance(node, Array_Node):
        if not node.elements:
            return 'array'
        first_elem_type = check(node.elements[0], symtab)
        for elem in node.elements[1:]:
            elem_type = check(elem, symtab)
            if elem_type != first_elem_type:
                raise TypeError(
                    f"Error : All elements in array must be of the same type. "
                    f"Expected '{first_elem_type}' type, but found '{elem_type}'"
                )
        return f"array[{first_elem_type}]"

    if isinstance(node, Index_Node):
        target_type = check(node.target, symtab)
        index_type = check(node.index, symtab)
        if index_type != 'int':
            raise TypeError(f"Error : Array Index must be integer")
        return 'any'

    if isinstance(node, Index_Assign_Node):
        target_type = check(node.target, symtab)
        index_type = check(node.index, symtab)
        value_type = check(node.value, symtab)
        if index_type != 'int':
            raise TypeError(f"Error : Array Index must be integer")
        return value_type

    if isinstance(node, Method_Call_Node):
        target_type = check(node.target, symtab)
        if node.args:
            for arg in node.args:
                check(arg, symtab)
        if node.method in ('push', 'pop'):
            if 'array[' in str(target_type) and ',' in str(target_type):
                raise TypeError(f"Error : Cannot {node.method} on fixed-size array")
        if node.method in ('len', 'length'):
            return 'int'
        elif node.method == 'pop':
            return 'any'
        return 'any'
