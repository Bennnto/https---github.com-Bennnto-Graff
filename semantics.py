from parse import (Assign_Node, Bool_Node, Int_Node, Type_Node, BinOps_Node, Str_Node, Variable_Node,
                   SingleOps_Node, Disp_Node, Entry_Node, While_Node, Return_Node, Function_Node,
                   Call_Node, For_Node, Float_Node, Param_Node, Array_Node, Index_Node, Index_Assign_Node,
                   Method_Call_Node, Array_Type_Node, Hash_Node, Hash_Type_Node, Throw_Node, Try_Ok_Node,
                   Assert_Node, Assert_Eq_Node, Attempt_Node, Lambda_Node, Box_Node, Move_Node, Ref_Node, Deref_Node,
                   Deref_Assign_Node, Fstr_Node, Match_Node, Case_Node, Ternary_Node, Timeline_Decl, Timeline_Index_Node,
                   Timeline_Rollback_Node, Enum_Node)

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
            if hasattr(node, '__dict__'):
                node.inferred_type = val_type
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
        
    if isinstance(t, Hash_Type_Node):
        key_t = get_type_name(t.key_type) if t.key_type else 'any'
        value_t = get_type_name(t.value_type) if t.value_type else 'any'
        return f"hash[{key_t}, {value_t}]"

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
    res = _check_node(node, symtab)
    if hasattr(node, '__dict__'):
        node.inferred_type = res
    return res

def _check_node(node, symtab):
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
        is_enum_left = isinstance(left_type, str) and left_type.startswith('enum[')
        is_enum_right = isinstance(right_type, str) and right_type.startswith('enum[')
        types_match = (left_type == right_type) or (left_type in ['int', 'float'] and is_enum_right) or (right_type in ['int', 'float'] and is_enum_left) or (is_enum_left and is_enum_right)

        if node.ops in ['>', '<', '>=', '<=', '==', '!=']:
            if left_type != 'any' and right_type != 'any' and not types_match:
                raise TypeError(f"Error : Type Error type of {left_type} not compatible with type of {right_type}")
            return 'bool'
        elif node.ops in ['&', '|']:
            if (left_type != 'bool' and left_type != 'any') or (right_type != 'bool' and right_type != 'any'):
                raise TypeError(f"Error : Logical operations require boolean types")
            return 'bool'
        else:
            if left_type != 'any' and right_type != 'any' and not types_match:
                raise TypeError(f"Error : Type Error type of {left_type} not compatible with type of {right_type}")
            if node.ops in ['+', '-', '*', '/', '%', '**'] and left_type not in ['int', 'float', 'str', 'any'] and not is_enum_left:
                raise TypeError(f"Error : Cannot perform {node.ops} on {left_type}")
            return left_type if left_type != 'any' else right_type
        
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
        if node.ident in ['int', 'to_int']:
            if node.parameter: check(node.parameter[0], symtab)
            return 'int'
        elif node.ident in ['float', 'to_float']:
            if node.parameter: check(node.parameter[0], symtab)
            return 'float'
        elif node.ident in ['str', 'to_str']:
            if node.parameter: check(node.parameter[0], symtab)
            return 'str'
        elif node.ident == 'abs':
            arg_type = check(node.parameter[0], symtab) if node.parameter else 'int'
            return arg_type

        func_symbol = symtab.get(node.ident)
        # Lambda-typed variables: allow calling without strict param checking
        if func_symbol == 'function':
            return 'any'
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
        if isinstance(target_type, str) and target_type.startswith('enum['):
            return 'int'
        if 'array[' in str(target_type) and index_type != 'int':
            raise TypeError(f"Error : Array Index must be integer")
        return 'any'

    if isinstance(node, Index_Assign_Node):
        target_type = check(node.target, symtab)
        index_type = check(node.index, symtab)
        value_type = check(node.value, symtab)
        if 'array[' in str(target_type) and index_type != 'int':
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
        elif node.method in ('equals', 'eq'):
            return 'bool'
        elif node.method == 'concat':
            return 'str'
        elif node.method == 'pop':
            return 'any'
        elif node.method == 'history':
            return 'array'
        return 'any'

    if isinstance(node, Hash_Node):
        if not node.elements :
            return 'hash'
        first_key_type = check(node.elements[0][0], symtab)
        first_value_type = check(node.elements[0][1], symtab)
        for elem in node.elements[1:]:
            key_type = check(elem[0], symtab)
            value_type = check(elem[1], symtab)
            if key_type != first_key_type:
                raise TypeError(f"Error : Key type expected {first_key_type} type got {key_type}")
            if value_type != first_value_type:
                raise TypeError(f"Error : Value type expected {first_value_type} type got {value_type}")
        return f"hash[{first_key_type}, {first_value_type}]"

    if isinstance(node, Throw_Node):
        check(node.expr, symtab)
        return None

    if isinstance(node, Try_Ok_Node):
        if isinstance(node.try_block, list):
            for stmt in node.try_block:
                check(stmt, symtab)
        else:
            check(node.try_block, symtab)

        symtab.push_scope()
        symtab.add(node.is_ok_ident, 'bool')
        symtab.add(node.err_ident, 'str')

        if isinstance(node.ok_block, list):
            for stmt in node.ok_block:
                check(stmt, symtab)
        else:
            check(node.ok_block, symtab)

        symtab.pop_scope()
        return None

    if isinstance(node, Assert_Node):
        condition_type = check(node.condition, symtab)
        if condition_type != 'bool':
            raise TypeError(f"Error : Assert condition must be boolean")
        return None

    if isinstance(node, Assert_Eq_Node):
        actual_type = check(node.actual, symtab)
        expected_type = check(node.expected, symtab)
        if actual_type != expected_type:
            raise TypeError(f"Error : Expected {expected_type} got {actual_type}")
        return expected_type

    if isinstance(node, Attempt_Node):
        retry_type = check(node.retry, symtab)
        if retry_type != 'int':
            raise TypeError(f"Error : Retry amount expected 'int' type got {retry_type} type")
        
        symtab.push_scope()
        if isinstance(node.attempt_block, list):
            for stmt in node.attempt_block:
                check(stmt, symtab)
        else:
            check(node.attempt_block, symtab)
        symtab.pop_scope()

        if node.fallback_block:
            symtab.push_scope()
            if isinstance(node.fallback_block, list):
                for stmt in node.fallback_block:
                    check(stmt, symtab)
            else:
                check(node.fallback_block, symtab)
        symtab.pop_scope()
        return None
    
    if isinstance(node, Lambda_Node):
        symtab.push_scope()
        for param in node.params:
            if isinstance(param, Param_Node):
                if param.type:
                    type_str = param.type.type if hasattr(param.type, 'type') else param.type
                else:
                    type_str = 'any'
                symtab.add(param.ident, type_str)
        body_type = check(node.body, symtab)
        symtab.pop_scope()
        return 'function'

    if isinstance(node, Box_Node):
        var_type = check(node.expr, symtab)
        return f"box[{var_type}]"
    
    if isinstance(node, Move_Node):
        return check(Variable_Node(ident=node.var_name), symtab)
     
    if isinstance(node, Ref_Node):
        val_type = check(Variable_Node(ident=node.var_name), symtab)
        is_mut = check(node.is_mutable, symtab)
        prefix = "ref_mut[" if node.is_mutable else "ref["
        return f"{prefix}{val_type}]"

    if isinstance(node, Deref_Node):
        ref_type = check(node.expr, symtab)
        if isinstance(ref_type, str):
            if ref_type.startswith("ref_mut["):
                return ref_type[8:-1]
            elif ref_type.startswith("ref["):
                return ref_type[4:-1]
            elif ref_type.startswith("box["):
                return ref_type[4:-1]
        return ref_type


    if isinstance(node, Deref_Assign_Node):
        target_type = check(node.target, symtab)
        value_type = check(node.value, symtab)
        if isinstance(target_type, str) and target_type.startswith("ref["):
            raise TypeError(f"Error : Cannot mutate through immutable reference {target_type} type")
        return None

    if isinstance(node, Fstr_Node):
        return 'str'


    if isinstance(node, Match_Node):
        target_type = check(node.target, symtab)
        for case in node.cases:
            is_wildcard = isinstance(case.pattern, Variable_Node) and case.pattern.ident == '_'
            if not is_wildcard:
                pattern_type = check(case.pattern, symtab)
                if target_type != 'any' and pattern_type != 'any' and target_type != pattern_type:
                    raise TypeError(f"Error : Case type {pattern_type} does not match target type {target_type}")
            symtab.push_scope()
            for stmt in case.body:
                check(stmt, symtab)
            symtab.pop_scope()
        return None

    if isinstance(node, Ternary_Node):
        cond_type = check(node.condition, symtab)
        if cond_type != 'bool':
            raise TypeError(f"Error : Condition expected boolean type got {cond_type} type")
        
        true_type = 'any'
        false_type = 'any'

        if node.true_block :
            symtab.push_scope()
            if isinstance(node.true_block, list):
                for stmt in node.true_block:
                    true_type=check(stmt, symtab)
            else:
                true_type=check(node.true_block, symtab)
            symtab.pop_scope()

        if node.false_block :
            symtab.push_scope()
            if isinstance(node.false_block, list):
                for stmt in node.false_block:
                    false_type=check(stmt, symtab)
            else:
                false_type= check(node.false_block, symtab)
            symtab.pop_scope()
        if true_type != 'any' and false_type != 'any' and true_type != false_type:
            raise TypeError(f"Error : Ternary branches must match types, got true branch '{true_type}' and false branch '{false_type}'")   
        return true_type if true_type != 'any' else false_type
    
    if isinstance(node, Timeline_Decl):
        ident_type = get_type_name(node.type) if node.type is not None else 'any'
        val_type = check(node.value, symtab)
        if val_type != 'any' and ident_type != 'any' and val_type != ident_type:
            raise TypeError(f"Error : Timeline {node.ident} declared as {ident_type} but got {val_type}")
        resolved = ident_type if ident_type != 'any' else val_type
        symtab.add(node.ident, resolved)
        return resolved

    if isinstance(node, Timeline_Index_Node):
        target_type = check(node.target, symtab)
        index_type = check(node.index, symtab)
        if index_type != 'int':
            raise TypeError(f"Error : Index type must be 'int' got {index_type}")
        return target_type

    if isinstance(node, Timeline_Rollback_Node):
        if not symtab.contains(node.ident):
            raise SemanticError(f"Error : Undefined timeline variable '{node.ident}'")
        ident_type = symtab.get(node.ident)

        if node.index is not None:
            index_type = check(node.index, symtab)
            if index_type != 'int':
                raise TypeError(f"Error : Index type must be 'int' got {index_type}")
        return ident_type
    
    if isinstance(node, Enum_Node):
        return visit_enum_node(node, symtab)
    
    
    
    
def visit_enum_node(node, symtab):
    #Validate Semantics rule for an Enum
    """
    1. Ensure that the Enum name is unique within scope
    2. Ensure member names within enum is unique
    3. Type_check explicit member initialization expression(if provided)
    4. Registers the Enum and its member into symbol table
    """
    
    # 1. check if Enum name already declared in current scope
    if symtab.current_scope_contains(node.name):
        raise SemanticError(f"Error : Enum {node.name} already declared in this scp")
    
    seen_members = set()
    
    # 2. Iterate through Enum members (tuple of (member_name, expr_node))
    for member in node.members:
        if isinstance(member, tuple):
            member_name, expr = member
        else :
            member_name = getattr(member, 'name', str(member)) 
            expr = getattr(member, 'value', None)
        # check for duplicate member name
        if member_name in seen_members:
            raise SemanticError(f"Error : Duplicate member {member_name} in Enum {node.name}")
        seen_members.add(member_name)
        
        if expr is not None :
            expr_type = check(expr, symtab)
            if expr_type not in ['int', 'str', 'any']:
                raise TypeError(f"Error : Enum member '{member_name} value must be in int or str got {expr_type}")
            
    enum_type = f"enum[{node.name}]"
    symtab.add(node.name, enum_type)
    return enum_type