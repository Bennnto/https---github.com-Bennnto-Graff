from opcodes import Opcode
from parse import (
    Int_Node, Str_Node, Bool_Node, Float_Node, Void_Node,
    BinOps_Node, SingleOps_Node, Assign_Node, Variable_Node,
    Disp_Node, Entry_Node, While_Node, Continue_Node, Break_Node,
    Return_Node, Function_Node, Call_Node, For_Node, Array_Node,
    Index_Node, Index_Assign_Node, Method_Call_Node, Hash_Node,
    Throw_Node, Try_Ok_Node, Assert_Node, Assert_Eq_Node, Attempt_Node,
    Lambda_Node, Box_Node, Move_Node, Ref_Node, Deref_Node, Deref_Assign_Node,
    Fstr_Node, Case_Node, Match_Node, Ternary_Node, Timeline_Decl,
    Timeline_Index_Node, Timeline_Rollback_Node, Enum_Node, Pub_Node,
    Bind_Node, Range_Node, For_Range_Node, Fix_Node, Struct_Decl_Node,
    Struct_Literal_Node, Field_Access_Node, Impl_Node, Drop_Node,
    Async_Node, Await_Node, Gaff_Node
)

class Instruction:
    def __init__(self, op: Opcode, arg=None):
        self.op = op
        self.arg = arg

    def __repr__(self):
        if self.arg is not None:
            return f"{self.op.name} {self.arg!r}"
        return f"{self.op.name}"

class Compiler:
    def __init__(self):
        self.instructions = []
        self.break_stack = []
        self.continue_stack = []

    def emit(self, op: Opcode, arg=None)->int:
        idx = len(self.instructions)
        self.instructions.append(Instruction(op, arg))
        return idx
    
    def patch(self, addr:int, target:int = None):
        if target is None:
            target = len(self.instructions)
        self.instructions[addr].arg = target

    def compile(self, ast) -> list[Instruction]:
        self.instructions = []
        if isinstance(ast, list):
            for stmt in ast :
                self.compile_node(stmt)
        else :
            self.compile_node(ast)
        self.emit(Opcode.OP_HALT)
        return self.instructions

    def optimize(self):
        """Peephole optimization pass over instructions"""
        optimized = []
        i = 0
        while i < len(self.instructions):
            inst1 = self.instructions[i]
            inst2 = self.instructions[i+1] if i+1 < len(self.instructions) else None
        # Pattern 1 OP_LOAD_CONST followed by OP_STORE_NAME
            if inst1.op == Opcode.OP_LOAD_CONST and inst2 and inst2.op == Opcode.OP_NAME:
                var_name = inst2.arg
                const_val = inst1.arg
                optimized.append(Instruction(Opcode.OP_STORE_CONST, (var_name, const_val)))
                i += 2
                continue
            
            optimized.append(inst1)
            i += 1
        self.instructions = optimized
        return self.instructions
            
    def compile_node(self, node):
        if node is None :
            return

        if isinstance(node, Int_Node):
            self.emit(Opcode.OP_LOAD_CONST, node.value)
        elif isinstance(node, Str_Node):
            self.emit(Opcode.OP_LOAD_CONST, node.value)
        elif isinstance(node, Bool_Node):
            self.emit(Opcode.OP_LOAD_CONST, node.value)
        elif isinstance(node, Float_Node):
            self.emit(Opcode.OP_LOAD_CONST, node.value)
        elif isinstance(node, Void_Node):
            self.emit(Opcode.OP_LOAD_CONST, None)

        elif isinstance(node, Variable_Node):
            self.emit(Opcode.OP_LOAD_NAME, node.ident)
        elif isinstance(node, Assign_Node):
            self.compile_node(node.value)
            self.emit(Opcode.OP_NAME, node.ident)
        elif isinstance(node, BinOps_Node):
            self.compile_node(node.left)
            self.compile_node(node.right)
            op_map = {
                '+' : Opcode.OP_ADD,
                '-' : Opcode.OP_SUB,
                '*' : Opcode.OP_MUL,
                '/' : Opcode.OP_DIV,
                '%' : Opcode.OP_MOD,
                '**' : Opcode.OP_POW,
                '==': Opcode.OP_EQ,
                '!=': Opcode.OP_NE,
                '<': Opcode.OP_LT,
                '>': Opcode.OP_GT,
                '<=': Opcode.OP_LE,
                '>=': Opcode.OP_GE,
                '&': Opcode.OP_AND,
                'and': Opcode.OP_AND,
                '|': Opcode.OP_OR,
                'or': Opcode.OP_OR,
                '<<': Opcode.OP_LSHIFT,
                '>>': Opcode.OP_RSHIFT,
                '^': Opcode.OP_BITXOR,
            }
            if node.ops in op_map:
                self.emit(op_map[node.ops])
            else :
                raise ValueError(f"Unknown binary Operator {node.ops}")

        elif isinstance(node, SingleOps_Node):
            self.compile_node(node.right)
            if node.ops == '-':
                self.emit(Opcode.OP_NEG)
            elif node.ops == '!':
                self.emit(Opcode.OP_NOT)
            elif node.ops == '~':
                self.emit(Opcode.OP_BITNOT)
        
        elif isinstance(node, Disp_Node):
            self.compile_node(node.expr)
            self.emit(Opcode.OP_DISP)

        
        elif isinstance(node, Entry_Node):
            if node.expr:
                self.compile_node(node.expr)
            else:
                self.emit(Opcode.OP_LOAD_CONST, "")
            self.emit(Opcode.OP_ENTRY)

        elif isinstance(node, While_Node):
            loop_start = len(self.instructions)
            self.compile_node(node.condition)
            jump_false_idx = self.emit(Opcode.OP_JUMP_IF_FALSE, 0)
            self.break_stack.append([])
            self.continue_stack.append([])


            if isinstance(node.while_block, list):
                for stmt in node.while_block:
                    self.compile_node(stmt)
            else :
                self.compile_node(node.while_block)

            for cont_addr in self.continue_stack.pop():
                self.patch(cont_addr, loop_start)
            self.emit(Opcode.OP_JUMP, loop_start)
            loop_end = len(self.instructions)
            self.patch(jump_false_idx, loop_end)

            for break_addr in self.break_stack.pop():
                self.patch(break_addr, loop_end)
         
        elif isinstance(node, For_Node):
            if node.init:
                self.compile_node(node.init)
            loop_start = len(self.instructions)
            if node.condition:
                self.compile_node(node.condition)
                jump_false_idx = self.emit(Opcode.OP_JUMP_IF_FALSE, 0)
            else :
                jump_false_id = None

            self.break_stack.append([])
            self.continue_stack.append([])
            if isinstance(node.for_block, list):
                for stmt in node.for_block:
                    self.compile_node(stmt)
            else:
                self.compile_node(node.for_block)
            
            update_start = len(self.instructions)
            for cont_addr in self.continue_stack.pop():
                self.patch(cont_addr, update_start)
            
            if node.update:
                self.compile_node(node.update)
            self.emit(Opcode.OP_JUMP, loop_start)

            loop_end = len(self.instructions)
            if jump_false_idx is not None :
                self.patch(jump_false_idx, loop_end)
            
            for break_addr in self.break_stack.pop():
                self.patch(break_addr, loop_end)
        
        elif isinstance(node, Break_Node):
            if self.break_stack:
                addr = self.emit(Opcode.OP_JUMP, 0)
                self.break_stack[-1].append(addr)

        elif isinstance(node, Continue_Node):
            if self.continue_stack:
                addr = self.emit(Opcode.OP_JUMP, 0)
                self.continue_stack[-1].append(addr)


        elif isinstance(node, Return_Node):
            if node.expr :
                self.compile_node(node.expr)
            else:
                self.emit(Opcode.OP_LOAD_CONST, None)
            self.emit(Opcode.OP_RETURN)

        elif isinstance(node, Match_Node):
            self.compile_node(node.target)
            jump_to_ends = []

            for case in node.cases:
                is_wildcard = isinstance(case.pattern, Variable_Node) and case.pattern.ident == '_'
                if not is_wildcard:
                    self.emit(Opcode.OP_DUP)
                    self.compile_node(case.pattern)
                    self.emit(Opcode.OP_EQ)
                    jump_next = self.emit(Opcode.OP_JUMP_IF_FALSE, 0)
                    self.emit(Opcode.OP_POP)
                    if isinstance(case.body, list):
                        for stmt in case.body:
                            self.compile_node(stmt)
                    else:
                        self.compile_node(case.body)
                    jump_to_ends.append(self.emit(Opcode.OP_JUMP, 0))
                    self.patch(jump_next, len(self.instructions))
                else:
                    self.emit(Opcode.OP_POP)
                    if isinstance(case.body, list):
                        for stmt in case.body:
                            self.compile_node(stmt)
                    else:
                        self.compile_node(case.body)
                    jump_to_ends.append(self.emit(Opcode.OP_JUMP, 0))
                    break

            self.emit(Opcode.OP_POP)
            end_addr = len(self.instructions)
            for jmp in jump_to_ends:
                self.patch(jmp, end_addr)
        
        elif isinstance(node, Function_Node):
            fn_compiler = Compiler()
            fn_body = node.body if isinstance(node.body, list) else [node.body]
            fn_code = fn_compiler.compile(fn_body)
            param_names = [p.ident if hasattr(p, 'ident') else p for p in (node.parameter or [])]

            defaults = {}
            if node.parameter:
                for p in node.parameter:
                    if hasattr(p, 'value') and p.value is not None:
                        from eval import eval_ast
                        from environment import Environment
                        defaults[p.ident] = eval_ast(p.value, Environment())

            func_data = {
                'name': node.ident,
                'params' : param_names,
                'defaults': defaults,
                'code': fn_code
            }
            self.emit(Opcode.OP_MAKE_FUNC, func_data)
            self.emit(Opcode.OP_NAME, node.ident)

        elif isinstance(node, Lambda_Node):
            lambda_compiler = Compiler()
            body_nodes = [Return_Node(node.body)] if not isinstance(node.body, list) else node.body
            lambda_code = lambda_compiler.compile(body_nodes)
            param_names = [p.ident if hasattr(p, 'ident') else p for p in (node.params or [])]

            lambda_data = {
                'params' : param_names,
                'code' : lambda_code,
            }
            self.emit(Opcode.OP_MAKE_FUNC, lambda_data)
        
        elif isinstance(node, Ternary_Node):
            self.compile_node(node.condition)
            jump_false_idx = self.emit(Opcode.OP_JUMP_IF_FALSE, 0)

            self.compile_node(node.true_block)
            jump_end_idx = self.emit(Opcode.OP_JUMP, 0)

            else_start = len(self.instructions)
            self.patch(jump_false_idx, else_start)
            self.compile_node(node.false_block)

            end_idx = len(self.instructions)
            self.patch(jump_end_idx, end_idx)

        elif isinstance(node, Call_Node):
            if node.parameter :
                for arg in node.parameter:
                    self.compile_node(arg)
            self.emit(Opcode.OP_CALL, (node.ident, len(node.parameter)if node.parameter else 0))

        elif isinstance(node, Method_Call_Node):
            self.compile_node(node.target)
            arg_count = 0
            if node.args:
                for arg in node.args:
                    self.compile_node(arg)
                arg_count = len(node.args)
            self.emit(Opcode.OP_CALL_METHOD, (node.method, arg_count))


        elif isinstance(node, Array_Node):
            if node.elements:
                for elem in node.elements:
                    self.compile_node(elem)
                self.emit(Opcode.OP_BUILD_ARRAY, len(node.elements))
            else:
                self.emit(Opcode.OP_BUILD_ARRAY, 0)
        
        elif isinstance(node, Hash_Node):
            if node.elements:
                for key, value in node.elements:
                    self.compile_node(key)
                    self.compile_node(value)
                self.emit(Opcode.OP_BUILD_HASH, len(node.elements))
            else:
                self.emit(Opcode.OP_BUILD_HASH, 0)

        elif isinstance(node, Index_Node):
            self.compile_node(node.target)
            if isinstance(node.index, Range_Node):
                if node.index.start:
                    self.compile_node(node.index.start)
                else:
                    self.emit(Opcode.OP_LOAD_CONST, None)
                if node.index.stop:
                    self.compile_node(node.index.stop)
                else:
                    self.emit(Opcode.OP_LOAD_CONST, None)
                self.emit(Opcode.OP_SLICE)
            else:
                self.compile_node(node.index)
                self.emit(Opcode.OP_BINARY_INDEX)

        elif isinstance(node, Index_Assign_Node):
            self.compile_node(node.target)
            self.compile_node(node.index)
            self.compile_node(node.value)
            self.emit(Opcode.OP_STORE_INDEX)
        
        elif isinstance(node, Throw_Node):
            self.compile_node(node.expr)
            self.emit(Opcode.OP_THROW)
        
        elif isinstance(node, Try_Ok_Node):
            try_idx = self.emit(Opcode.OP_TRY, 0)
            self.compile_node(node.try_block)
            self.emit(Opcode.OP_END_TRY)

            jump_ok_end = self.emit(Opcode.OP_JUMP, 0)
            handler_addr = len(self.instructions)
            self.patch(try_idx, handler_addr)

            self.emit(Opcode.OP_PUSH_OK_RESULT, (node.is_ok_ident, node.err_ident))  
            self.compile_node(node.ok_block)
            self.patch(jump_ok_end, len(self.instructions))

        elif isinstance(node, Assert_Node):
            self.compile_node(node.condition)
            if node.message:
                self.compile_node(node.message)
            else: 
                self.emit(Opcode.OP_LOAD_CONST, "Assertion Failed")
            self.emit(Opcode.OP_ASSERT)

        elif isinstance(node, Assert_Eq_Node):
            self.compile_node(node.actual)
            self.compile_node(node.expected)
            self.emit(Opcode.OP_EQ)
            self.emit(Opcode.OP_LOAD_CONST, "Assertion Eq Failed")
            self.emit(Opcode.OP_ASSERT)

        elif isinstance(node, Attempt_Node):
            self.compile_node(node.retry)
            attempt_try_idx = self.emit(Opcode.OP_TRY, 0)
            self.compile_node(node.attempt_block)
            self.emit(Opcode.OP_END_TRY)
            jump_end = self.emit(Opcode.OP_JUMP, 0)

            fallback_addr = len(self.instructions)
            self.patch(attempt_try_idx, fallback_addr)
            self.compile_node(node.fallback_block)
            self.patch(jump_end, len(self.instructions))

        elif isinstance(node, Box_Node):
            self.compile_node(node.expr)
            self.emit(Opcode.OP_BOX)

        elif isinstance(node, Move_Node):
            self.emit(Opcode.OP_MOVE, node.var_name)

        elif isinstance(node, Ref_Node):
            self.emit(Opcode.OP_REF, (node.var_name, node.is_mutable))

        elif isinstance(node, Deref_Node):
            self.compile_node(node.expr)
            self.emit(Opcode.OP_DEREF)

        elif isinstance(node, Deref_Assign_Node):
            self.compile_node(node.target)
            self.compile_node(node.value)
            self.emit(Opcode.OP_DEREF_ASSIGN)
        
        elif isinstance(node, Fstr_Node):
            raw = getattr(node, 'raw', '')
            if not raw:
                self.emit(Opcode.OP_LOAD_CONST, "")
            else:
                last_end = 0
                parts_count = 0
                import re
                from parse import parser
                from lexicals import lexer
                for match in re.finditer(r'\{([^}]+)\}', raw):
                    prefix = raw[last_end:match.start()]
                    if prefix:
                        self.emit(Opcode.OP_LOAD_CONST, prefix)
                        if parts_count > 0:
                            self.emit(Opcode.OP_ADD)
                        parts_count += 1
                    
                    expr_text = match.group(1).strip()
                    fmt_spec = None
                    if ':' in expr_text and not expr_text.startswith('::'):
                        expr_text, fmt_spec = expr_text.split(':', 1)
                    
                    expr_ast = parser.parse(expr_text, lexer=lexer)
                    target_ast = expr_ast[0] if isinstance(expr_ast, list) and len(expr_ast) > 0 else expr_ast
                    self.compile_node(target_ast)
                    if fmt_spec:
                        self.emit(Opcode.OP_FORMAT_VAL, fmt_spec)
                    else:
                        self.emit(Opcode.OP_TO_STR)
                    if parts_count > 0:
                        self.emit(Opcode.OP_ADD)
                    parts_count += 1
                    last_end = match.end()
                
                suffix = raw[last_end:]
                if suffix:
                    self.emit(Opcode.OP_LOAD_CONST, suffix)
                    if parts_count > 0:
                        self.emit(Opcode.OP_ADD)

        elif isinstance(node, Timeline_Decl):
            self.compile_node(node.value)
            self.emit(Opcode.OP_TIMELINE_DECL, node.ident)

        elif isinstance(node, Timeline_Index_Node):
            self.compile_node(node.target)
            self.compile_node(node.index)
            self.emit(Opcode.OP_TIMELINE_INDEX)
            
        elif isinstance(node, Timeline_Rollback_Node):
            if node.index is not None:
                self.compile_node(node.index)
            else:
                self.emit(Opcode.OP_LOAD_CONST, None)
            self.emit(Opcode.OP_ROLLBACK, node.ident)
            
        elif isinstance(node, Enum_Node):
            self.compile_node(Str_Node(node.name))

            if node.members:
                for member in node.members:
                    if isinstance(member, tuple):
                       member_name, expr = member
                    else:
                       member_name = getattr(member, 'name', str(member))
                       expr = getattr(member, 'value', None)
                    
                    self.compile_node(Str_Node(member_name))
                    if expr is not None :
                        self.compile_node(expr)
                    else : 
                        self.compile_node(Void_Node())
                    
                self.emit(Opcode.OP_BUILD_ENUM, len(node.members))
            else:
                self.emit(Opcode.OP_BUILD_ENUM, 0)
            
        elif isinstance(node, Pub_Node):
            self.compile_node(node.node)
            symbol_name = getattr(node.node, 'ident', None)
            self.emit(Opcode.OP_PUB, symbol_name)

        elif isinstance(node, Bind_Node):
            self.compile_node(node.path)
            if isinstance(node.alias, list) or node.alias == "*":
                alias_name = node.alias
            else:
                alias_name = getattr(node.alias, 'ident', str(node.alias))
            self.emit(Opcode.OP_BIND, alias_name)
            
    
        elif isinstance(node, Range_Node):
            if node.amount is not None :
                self.compile_node(node.amount)
                self.emit(Opcode.OP_RANGE, 1)
            else: 
                self.compile_node(node.start)
                self.compile_node(node.stop)
                if node.step is not None:
                    self.compile_node(node.step)
                    self.emit(Opcode.OP_RANGE, 3)
                else:
                    self.emit(Opcode.OP_RANGE, 2)
            
        elif isinstance(node, For_Range_Node):
            # Compile Range expression
            self.compile_node(node.range)
        
            # Create iterator
            self.emit(Opcode.OP_ITER_NEW)
            
            # Jump to condition check
            loop_start = len(self.instructions)

            # Check if iterator is done
            jump_if_done = self.emit(Opcode.OP_ITER_DONE, 0)
            
            # Load next value from iterater
            self.emit(Opcode.OP_ITER_NEXT)
            
            # store in loop variable if exists
            if node.ident:
                self.emit(Opcode.OP_NAME, node.ident)
                
            self.break_stack.append([])
            self.continue_stack.append([])
            
            if isinstance(node.for_block, list):
                for stmt in node.for_block:
                    self.compile_node(stmt)
            else:
                self.compile_node(node.for_block)
            
            # Handle Continue (jump back to condition check)
            for cont_addr in self.continue_stack.pop():
                self.patch(cont_addr, loop_start)
            
            # Jump back to start of loop
            self.emit(Opcode.OP_JUMP, loop_start)
            
            # Patch the "done" jump to here (end of loop)
            loop_end = len(self.instructions)
            self.patch(jump_if_done, loop_end)

            # Handle break statements
            for break_addr in self.break_stack.pop():
                self.patch(break_addr, loop_end)
                
        elif isinstance(node, Fix_Node):
            self.compile_node(node.value)
            self.emit(Opcode.OP_NAME, node.ident if isinstance(node.ident, str) else node.ident.ident)
        
        elif isinstance(node, Struct_Decl_Node):
            pass

        elif isinstance(node, Struct_Literal_Node):
            field_name = list(node.field_values.keys())
            for fname in field_name:
                self.compile_node(node.field_values[fname])

            self.emit(Opcode.OP_BUILD_STRUCT, (node.name, len(field_name), field_name))

        elif isinstance(node, Field_Access_Node):
            self.compile_node(node.target)
            self.emit(Opcode.OP_GET_FIELD, node.field)

        elif isinstance(node, Impl_Node):
            for method in node.methods:
                self.compile_node(method)
                    
        elif isinstance(node, Drop_Node):
            self.emit(Opcode.OP_DROP, node.target)

        elif isinstance(node, Async_Node):
            fn = node.func
            fn_compiler = Compiler()
            fn_body = fn.body if isinstance(fn.body, list) else [fn.body]
            fn_code = fn_compiler.compile(fn_body)
            param_names = [p.ident if hasattr(p, 'ident') else p for p in (fn.parameter or [])]

            defaults = {}
            if fn.parameter:
                for p in fn.parameter:
                    if hasattr(p, 'value') and p.value is not None:
                        from eval import eval_ast
                        from environment import Environment
                        defaults[p.ident] = eval_ast(p.value, Environment())

            func_data = {
                'name': fn.ident,
                'params': param_names,
                'defaults': defaults,
                'code': fn_code,
                'is_async': True,
            }
            self.emit(Opcode.OP_MAKE_ASYNC_FUNC, func_data)
            self.emit(Opcode.OP_NAME, fn.ident)

        elif isinstance(node, Await_Node):
            self.compile_node(node.expr)   # compile the call → pushes future onto stack
            self.emit(Opcode.OP_AWAIT)     # wait for the thread to finish

        elif isinstance(node, Gaff_Node):
            constraint_compiler = Compiler()
            body_nodes = node.gaff_block if isinstance(node.gaff_block, list) else [node.gaff_block]
            
            # The constraint block should return its result. If the block doesn't explicitly return,
            # we need it to evaluate and leave the result on the stack.
            # But normally statements pop results. Since we're keeping it simple, we compile it,
            # and in the VM we can just check what it evaluates to, or assume it uses OP_RETURN.
            # Let's compile it just like a lambda.
            constraint_code = constraint_compiler.compile(body_nodes)
            
            constraint_data = {
                'target': node.ident,
                'code': constraint_code,
            }
            self.emit(Opcode.OP_GAFF_CONSTRAINT, constraint_data)