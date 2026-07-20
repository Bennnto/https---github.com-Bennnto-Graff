from parse import Assign_Node, Int_Node, Type_Node, BinOps_Node, Str_Node

class SemanticError(Exception):
    pass
class TypeError(Exception):
    pass

class SymbolTable:
    def __init__(self):
        self.scopes = [{}]
        
    # Enter new block scope for if / loop/ function.    
    def push_scope(self):
        self.scopes.append({})
        
    # Exit current block scope 
    def pop_scope(self):
        self.scopes.pop()
    
    # Add symbol to current scope. Raise error if already exist.
    def add(self, name, type_node):
        if name in self.scopes[-1]:
            raise SemanticError(f"Error : Variable {name} already defined in this scope")
        self.scopes[-1][name] = type_node
    
    # Lookup symbols, searching outer scopes. Raise if not found.
    def get(self, name):
        for scope in reversed(self.scopes):
            if name in scope :
                return scope[name]
            raise SemanticError(f"Error : Variable {name} not declared")
        
    # Check current scope only (no outer scope search)
    def current_scope_contain(self, name):
        return name in self.scopes[-1]
    
    # Validate semantics and types with scoper symbol table. symtab: symbol table isinstance( pass same instance through recursion )
    def check(node, symtab):
        if isinstance(node, Int_Node):
            return 'int'
        if isinstance(node, Str_Node):
            return 'str'
        if isinstance(node, Type_Node):
            return node.type
        
        if isinstance(node, Assign_Node):
            value_type = check(node.value, symtab)
            declared_type = node.type.type if node.type else 'int'
            if value_type != declared_type:
                raise TypeError(f"Error : Type Error type of {node.value} not compatible with {node.type} expected {node.type}")
            if symtab.current_scope_contain(node.ident):
                raise SemanticError(f"Error : {node.ident} already defined in this scope")
            symtab.add(node.ident, declared_type)
            return declared_type 
        
        if isinstance(node, BinOps_Node):
            left_type = check(node.left, symtab)
            right_type = check(node.right, symtab)
            if left_type != right_type:
                raise TypeError(f"Error : Type Error type of {node.left} not compatible with type of {node.right}")
            if left_type != 'int':
                raise TypeError(f"Error : Cannot perform arithmetic on {left_type}")
            return left_type
        
        
        
        
# Map Runtime values to your type systems
def get_type(value):
    if isinstance(value, int):
        return 'int'
    return type(value).__name__

    