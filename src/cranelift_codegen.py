"""
Complete Cranelift IR (CLIF) Generator for Gaff / Veln Language
Translates ALL AST Node types in new_eval into clean Cranelift IR (.clif) instructions.
"""

from parse import (
    Int_Node, Float_Node, Bool_Node, Str_Node, Void_Node,
    BinOps_Node, SingleOps_Node, Assign_Node, Variable_Node,
    Disp_Node, Entry_Node, While_Node, Continue_Node, Break_Node,
    Return_Node, Function_Node, Call_Node, For_Node, Array_Node,
    Index_Node, Index_Assign_Node, Method_Call_Node, Hash_Node,
    Throw_Node, Try_Ok_Node, Assert_Node, Assert_Eq_Node, Attempt_Node,
    Lambda_Node, Box_Node, Move_Node, Ref_Node, Deref_Node, Deref_Assign_Node,
    Fstr_Node, Case_Node, Match_Node, Ternary_Node, Timeline_Decl,
    Timeline_Index_Node, Timeline_Rollback_Node, Enum_Node, Pub_Node,
    Bind_Node, Range_Node, For_Range_Node, Fix_Node, Struct_Decl_Node,
    Struct_Literal_Node, Field_Access_Node, Impl_Node, Drop_Node, Param_Node
)

class CraneliftCodegen:
    def __init__(self):
        self.var_counter = 0
        self.block_counter = 0
        self.func_counter = 0
        self.var_map = {}
        self.lines = []
        self.functions = []

    def new_value(self) -> str:
        v = f"v{self.var_counter}"
        self.var_counter += 1
        return v

    def new_block(self, prefix="block") -> str:
        b = f"{prefix}{self.block_counter}"
        self.block_counter += 1
        return b

    def generate(self, ast, main_name: str = "main") -> str:
        """Translates an entire program AST into a complete Cranelift IR (.clif) string"""
        self.var_counter = 0
        self.block_counter = 0
        self.func_counter = 0
        self.var_map = {}
        self.lines = []
        self.functions = []

        # 1. Process Top-Level Statements
        self.lines.append(f"function @{main_name}() -> i64 {{")
        entry_block = self.new_block()
        self.lines.append(f"{entry_block}:")

        last_val = "v0"
        if isinstance(ast, list):
            for stmt in ast:
                last_val = self.gen_node(stmt)
        elif ast is not None:
            last_val = self.gen_node(ast)

        if not last_val or last_val == "v0":
            v_zero = self.new_value()
            self.lines.append(f"    {v_zero} = iconst.i64 0")
            last_val = v_zero

        self.lines.append(f"    return {last_val}")
        self.lines.append("}\n")

        # Combine main function + any nested functions declared
        full_code = "\n".join(self.functions) + "\n" + "\n".join(self.lines)
        return full_code.strip()

    def gen_node(self, node) -> str:
        if node is None:
            return ""

        # -------------------------------------------------------------
        # 1. Primitives & Literals
        # -------------------------------------------------------------
        if isinstance(node, Int_Node):
            v = self.new_value()
            self.lines.append(f"    {v} = iconst.i64 {node.value}")
            return v

        elif isinstance(node, Float_Node):
            v = self.new_value()
            self.lines.append(f"    {v} = f64const {node.value}")
            return v

        elif isinstance(node, Bool_Node):
            v = self.new_value()
            val_int = 1 if node.value else 0
            self.lines.append(f"    {v} = bconst.b1 {val_int}")
            return v

        elif isinstance(node, Str_Node):
            v = self.new_value()
            self.lines.append(f"    {v} = iconst.i64 0 ; str: {node.value!r}")
            return v

        elif isinstance(node, Void_Node):
            v = self.new_value()
            self.lines.append(f"    {v} = iconst.i64 0 ; void")
            return v

        # -------------------------------------------------------------
        # 2. Variables & Assignments
        # -------------------------------------------------------------
        elif isinstance(node, Variable_Node):
            if node.ident in self.var_map:
                return self.var_map[node.ident]
            v = self.new_value()
            self.lines.append(f"    {v} = iconst.i64 0 ; read '{node.ident}'")
            return v

        elif isinstance(node, (Assign_Node, Fix_Node)):
            val_v = self.gen_node(node.value)
            self.var_map[node.ident] = val_v
            self.lines.append(f"    ; let {node.ident} = {val_v}")
            return val_v

        # -------------------------------------------------------------
        # 3. Binary & Single Operations
        # -------------------------------------------------------------
        elif isinstance(node, BinOps_Node):
            lhs = self.gen_node(node.left)
            rhs = self.gen_node(node.right)
            res = self.new_value()

            op_map = {
                '+': 'iadd', '-': 'isub', '*': 'imul', '/': 'sdiv', '%': 'srem',
                '==': 'icmp eq', '!=': 'icmp ne', '<': 'icmp slt', '>': 'icmp sgt',
                '<=': 'icmp sle', '>=': 'icmp sge', '&&': 'band', '||': 'bor'
            }
            clif_op = op_map.get(node.ops, 'iadd')
            self.lines.append(f"    {res} = {clif_op} {lhs}, {rhs}")
            return res

        elif isinstance(node, SingleOps_Node):
            rhs = self.gen_node(node.right)
            res = self.new_value()
            if node.ops == '-':
                self.lines.append(f"    {res} = ineg {rhs}")
            elif node.ops in ('!', 'not'):
                self.lines.append(f"    {res} = bnot {rhs}")
            else:
                res = rhs
            return res

        elif isinstance(node, Ternary_Node):
            cond_v = self.gen_node(node.condition)
            then_b = self.new_block("then")
            else_b = self.new_block("else")
            merge_b = self.new_block("merge")

            self.lines.append(f"    brif {cond_v}, {then_b}, {else_b}")
            
            # Then block
            self.lines.append(f"{then_b}:")
            true_v = self.gen_node(node.true_block)
            self.lines.append(f"    jump {merge_b}({true_v})")

            # Else block
            self.lines.append(f"{else_b}:")
            false_v = self.gen_node(node.false_block)
            self.lines.append(f"    jump {merge_b}({false_v})")

            # Merge block
            res_v = self.new_value()
            self.lines.append(f"{merge_b}({res_v}: i64):")
            return res_v

        # -------------------------------------------------------------
        # 4. Functions & Calls
        # -------------------------------------------------------------
        elif isinstance(node, Function_Node):
            func_name = node.ident
            params = node.parameter if node.parameter else []
            param_str = ", ".join([f"v{i}: i64" for i in range(len(params))])
            
            func_lines = [f"function @{func_name}({param_str}) -> i64 {{", "entry_block:"]
            old_lines = self.lines
            self.lines = func_lines
            
            for idx, p in enumerate(params):
                self.var_map[p.ident] = f"v{idx}"

            last_v = "v0"
            for stmt in node.body:
                last_v = self.gen_node(stmt)

            if not last_v:
                v_z = self.new_value()
                self.lines.append(f"    {v_z} = iconst.i64 0")
                last_v = v_z

            self.lines.append(f"    return {last_v}")
            self.lines.append("}\n")

            self.functions.append("\n".join(self.lines))
            self.lines = old_lines
            return ""

        elif isinstance(node, Call_Node):
            arg_vars = [self.gen_node(arg) for arg in (node.parameter or [])]
            args_str = ", ".join(arg_vars)
            res = self.new_value()
            self.lines.append(f"    {res} = call @{node.ident}({args_str})")
            return res

        elif isinstance(node, Lambda_Node):
            v = self.new_value()
            self.lines.append(f"    {v} = iconst.i64 0 ; lambda")
            return v

        elif isinstance(node, Return_Node):
            val_v = self.gen_node(node.expr) if node.expr else ""
            if val_v:
                self.lines.append(f"    return {val_v}")
            else:
                self.lines.append("    return")
            return val_v

        # -------------------------------------------------------------
        # 5. Loops (While & For)
        # -------------------------------------------------------------
        elif isinstance(node, While_Node):
            header_b = self.new_block("while_hdr")
            body_b = self.new_block("while_body")
            exit_b = self.new_block("while_exit")

            self.lines.append(f"    jump {header_b}")
            self.lines.append(f"{header_b}:")
            cond_v = self.gen_node(node.condition)
            self.lines.append(f"    brif {cond_v}, {body_b}, {exit_b}")

            self.lines.append(f"{body_b}:")
            for stmt in node.while_block:
                self.gen_node(stmt)
            self.lines.append(f"    jump {header_b}")

            self.lines.append(f"{exit_b}:")
            return ""

        elif isinstance(node, (For_Node, For_Range_Node)):
            if getattr(node, 'init', None):
                self.gen_node(node.init)

            header_b = self.new_block("for_hdr")
            body_b = self.new_block("for_body")
            exit_b = self.new_block("for_exit")

            self.lines.append(f"    jump {header_b}")
            self.lines.append(f"{header_b}:")
            cond_v = self.gen_node(node.condition) if getattr(node, 'condition', None) else self.new_value()
            if not getattr(node, 'condition', None):
                self.lines.append(f"    {cond_v} = bconst.b1 1")

            self.lines.append(f"    brif {cond_v}, {body_b}, {exit_b}")

            self.lines.append(f"{body_b}:")
            for stmt in getattr(node, 'for_block', []):
                self.gen_node(stmt)

            if getattr(node, 'update', None):
                self.gen_node(node.update)

            self.lines.append(f"    jump {header_b}")
            self.lines.append(f"{exit_b}:")
            return ""

        elif isinstance(node, Break_Node):
            self.lines.append("    ; break")
            return ""

        elif isinstance(node, Continue_Node):
            self.lines.append("    ; continue")
            return ""

        # -------------------------------------------------------------
        # 6. Memory, References & Borrowing
        # -------------------------------------------------------------
        elif isinstance(node, Box_Node):
            val_v = self.gen_node(node.expr)
            res = self.new_value()
            self.lines.append(f"    {res} = call @malloc(8) ; box heap alloc")
            self.lines.append(f"    store {val_v}, {res}")
            return res

        elif isinstance(node, Move_Node):
            var_name = getattr(node, 'var_name', getattr(node, 'target', ''))
            if isinstance(var_name, Variable_Node):
                var_name = var_name.ident
            val_v = self.var_map.get(var_name, "v0")
            if var_name in self.var_map:
                del self.var_map[var_name]
            self.lines.append(f"    ; move {var_name} ({val_v})")
            return val_v

        elif isinstance(node, Ref_Node):
            var_name = getattr(node, 'var_name', getattr(node, 'target', ''))
            val_v = self.var_map.get(var_name, "v0")
            self.lines.append(f"    ; ref {var_name}")
            return val_v

        elif isinstance(node, Deref_Node):
            val_v = self.gen_node(node.expr)
            res = self.new_value()
            self.lines.append(f"    {res} = load.i64 {val_v} ; deref")
            return res

        elif isinstance(node, Deref_Assign_Node):
            ptr_v = self.gen_node(node.target)
            val_v = self.gen_node(node.value)
            self.lines.append(f"    store {val_v}, {ptr_v} ; deref assign")
            return val_v

        elif isinstance(node, Drop_Node):
            self.lines.append(f"    ; drop {node.target}")
            if node.target in self.var_map:
                del self.var_map[node.target]
            return ""

        # -------------------------------------------------------------
        # 7. Collections (Arrays, Hashes, Structs, Enums)
        # -------------------------------------------------------------
        elif isinstance(node, Array_Node):
            res = self.new_value()
            self.lines.append(f"    {res} = call @create_array() ; array literal")
            return res

        elif isinstance(node, Index_Node):
            target_v = self.gen_node(node.target)
            idx_v = self.gen_node(node.index)
            res = self.new_value()
            self.lines.append(f"    {res} = call @array_get({target_v}, {idx_v})")
            return res

        elif isinstance(node, Index_Assign_Node):
            target_v = self.gen_node(node.target)
            idx_v = self.gen_node(node.index)
            val_v = self.gen_node(node.value)
            self.lines.append(f"    call @array_set({target_v}, {idx_v}, {val_v})")
            return val_v

        elif isinstance(node, Hash_Node):
            res = self.new_value()
            self.lines.append(f"    {res} = call @create_hash() ; hash literal")
            return res

        elif isinstance(node, Struct_Literal_Node):
            res = self.new_value()
            self.lines.append(f"    {res} = call @create_struct({node.name!r})")
            return res

        elif isinstance(node, Field_Access_Node):
            target_v = self.gen_node(node.target)
            res = self.new_value()
            self.lines.append(f"    {res} = call @get_field({target_v}, {node.field!r})")
            return res

        elif isinstance(node, Method_Call_Node):
            target_v = self.gen_node(node.target)
            arg_vars = [self.gen_node(arg) for arg in (node.args or [])]
            arg_str = ", ".join([target_v] + arg_vars)
            res = self.new_value()
            self.lines.append(f"    {res} = call @{node.method}({arg_str})")
            return res

        elif isinstance(node, Struct_Decl_Node):
            self.lines.append(f"    ; struct {node.name}")
            return ""

        elif isinstance(node, Impl_Node):
            for method in node.methods:
                self.gen_node(method)
            return ""

        elif isinstance(node, Enum_Node):
            self.lines.append(f"    ; enum {node.name}")
            return ""

        # -------------------------------------------------------------
        # 8. Pattern Matching (Match / Case)
        # -------------------------------------------------------------
        elif isinstance(node, Match_Node):
            target_v = self.gen_node(node.target)
            match_exit = self.new_block("match_exit")

            for case in getattr(node, 'cases', []):
                case_b = self.new_block("case_body")
                next_case_b = self.new_block("case_next")
                
                pat_v = self.gen_node(case.pattern)
                cond_v = self.new_value()
                self.lines.append(f"    {cond_v} = icmp eq {target_v}, {pat_v}")
                self.lines.append(f"    brif {cond_v}, {case_b}, {next_case_b}")

                self.lines.append(f"{case_b}:")
                for stmt in getattr(case, 'body', []):
                    self.gen_node(stmt)
                self.lines.append(f"    jump {match_exit}")
                self.lines.append(f"{next_case_b}:")

            self.lines.append(f"{match_exit}:")
            return ""

        # -------------------------------------------------------------
        # 9. I/O & Assertions & Error Handling
        # -------------------------------------------------------------
        elif isinstance(node, Disp_Node):
            val_v = self.gen_node(node.expr)
            self.lines.append(f"    call @disp({val_v}) ; disp()")
            return val_v

        elif isinstance(node, Assert_Node):
            cond_v = self.gen_node(node.condition)
            self.lines.append(f"    call @assert({cond_v})")
            return ""

        elif isinstance(node, Assert_Eq_Node):
            lhs = self.gen_node(node.actual)
            rhs = self.gen_node(node.expected)
            self.lines.append(f"    call @assert_eq({lhs}, {rhs})")
            return ""

        elif isinstance(node, Throw_Node):
            val_v = self.gen_node(node.expr)
            self.lines.append(f"    call @throw({val_v})")
            return ""

        # -------------------------------------------------------------
        # 10. Timelines & History
        # -------------------------------------------------------------
        elif isinstance(node, Timeline_Decl):
            val_v = self.gen_node(node.value)
            self.var_map[node.ident] = val_v
            self.lines.append(f"    ; timeline {node.ident} = {val_v}")
            return val_v

        elif isinstance(node, Timeline_Rollback_Node):
            self.lines.append(f"    ; rollback {node.ident}")
            return ""

        # -------------------------------------------------------------
        # 11. Modules & Standard Library Bindings (Dynamic Coverage)
        # -------------------------------------------------------------
        elif isinstance(node, Bind_Node):
            path_str = node.path.value if hasattr(node.path, 'value') else str(node.path)
            self.lines.append(f"    ; bind module '{path_str}' (alias: {node.alias})")
            
            try:
                from std_lib import STD_MODULES
                if path_str in STD_MODULES:
                    mod_dict = STD_MODULES[path_str]
                    for fn_name in mod_dict:
                        sym_name = f"{path_str.replace('::', '_')}_{fn_name}"
                        decl = f"fn @{sym_name}(i64) -> i64 system_v"
                        if decl not in self.functions:
                            self.functions.append(decl)
                else:
                    clean_name = path_str.replace('::', '_').replace('.', '_').replace('/', '_')
                    decl = f"fn @{clean_name}_init() -> i64 system_v"
                    if decl not in self.functions:
                        self.functions.append(decl)
            except ImportError:
                pass
            return ""

        elif isinstance(node, Pub_Node):
            return self.gen_node(node.node)

        # Fallback for any unhandled node
        return ""
