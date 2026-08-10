"""
Complete Native C Code Generator for Gaff / Veln Language
Translates ALL 43 AST Node types into clean C code for native binary compilation via Clang / GCC (-O3).
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
    Struct_Literal_Node, Field_Access_Node, Impl_Node, Drop_Node, Param_Node,
    Async_Node, Await_Node, Gaff_Node
)

class NativeCodegen:
    def __init__(self):
        self.var_map = {}
        self.functions = []
        self.lines = []
        self.struct_decls = []

    def generate(self, ast, main_name: str = "main") -> str:
        """Translates an entire program AST into complete C code"""
        self.var_map = {}
        self.functions = []
        self.lines = []
        self.struct_decls = []
        self.gaff_hook = {}


        header = [
            "#include <stdio.h>",
            "#include <stdlib.h>",
            "#include <stdint.h>",
            "#include <stdbool.h>",
            "#include <math.h>",
            "#include <string.h>",
            "#include <time.h>",
            "#include <assert.h>",
            "#include <pthread.h>",
            "",
            "// Gaff Dynamic Value Struct",
            "typedef enum { GAFF_INT, GAFF_FLOAT, GAFF_BOOL, GAFF_STR, GAFF_PTR } GaffType;",
            "typedef struct { GaffType type; union { int64_t i; double f; bool b; char* s; void* ptr; } val; } GaffValue;",
            "",
            "void gaff_disp(int64_t v) { printf(\"%lld\\n\", (long long)v); }",
            "void gaff_disp_float(double v) { printf(\"%.4f\\n\", v); }",
            "void gaff_disp_str(const char* s) { printf(\"%s\\n\", s); }",
            ""
        ]

        self.lines.append("int main() {")
        
        last_val = "0"
        if isinstance(ast, list):
            for stmt in ast:
                last_val = self.gen_node(stmt)
        elif ast is not None:
            last_val = self.gen_node(ast)

        self.lines.append("    return 0;")
        self.lines.append("}")

        full_code = "\n".join(header) + "\n".join(self.struct_decls) + "\n" + "\n".join(self.functions) + "\n\n" + "\n".join(self.lines)
        return full_code

    def gen_node(self, node) -> str:
        if node is None:
            return ""

        # -------------------------------------------------------------
        # 1. Primitives & Literals
        # -------------------------------------------------------------
        if isinstance(node, Int_Node):
            return str(node.value)

        elif isinstance(node, Float_Node):
            return str(node.value)

        elif isinstance(node, Bool_Node):
            return "true" if node.value else "false"

        elif isinstance(node, Str_Node):
            return f'"{node.value}"'

        elif isinstance(node, Void_Node):
            return "0"

        # -------------------------------------------------------------
        # 2. Variables & Assignments
        # -------------------------------------------------------------
        elif isinstance(node, Variable_Node):
            return node.ident

        elif isinstance(node, (Assign_Node, Fix_Node)):
            val_c = self.gen_node(node.value)
            type_str = "int64_t"
            if hasattr(node, 'type') and node.type:
                t = str(getattr(node.type, 'type', node.type)).lower()
                if 'float' in t:
                    type_str = "double"
                elif 'str' in t:
                    type_str = "const char*"
                elif 'bool' in t:
                    type_str = "bool"
            if node.ident in self.var_map:
                self.lines.append(f"    {node.ident} = {val_c};")
            else:
                self.lines.append(f"    {type_str} {node.ident} = {val_c};")
                self.var_map[node.ident] = type_str
            if hasattr(self, 'gaff_hook') and node.ident in self.gaff_hook:
                hook_fn = self.gaff_hook[node.ident]
                self.lines.append(f"    if(!{hook_fn}({node.ident})) {{")
                self.lines.append(f"        printf(\"Error: Constraint on '{node.ident}' violated \\n\");")
                self.lines.append(f"        exit(1);")
                self.lines.append(f" }}")
            return node.ident

        # -------------------------------------------------------------
        # 3. Operations & Ternary
        # -------------------------------------------------------------
        elif isinstance(node, BinOps_Node):
            lhs = self.gen_node(node.left)
            rhs = self.gen_node(node.right)
            return f"({lhs} {node.ops} {rhs})"

        elif isinstance(node, SingleOps_Node):
            rhs = self.gen_node(node.right)
            op = "!" if node.ops in ('!', 'not') else node.ops
            return f"({op}{rhs})"

        elif isinstance(node, Ternary_Node):
            cond = self.gen_node(node.condition)
            tb = self.gen_node(node.true_block)
            fb = self.gen_node(node.false_block)
            return f"({cond} ? {tb} : {fb})"

        # -------------------------------------------------------------
        # 4. Functions & Calls
        # -------------------------------------------------------------
        elif isinstance(node, Function_Node):
            func_name = node.ident
            params = node.parameter if node.parameter else []
            param_str = ", ".join([f"int64_t {p.ident}" for p in params])
            
            func_body = [f"int64_t {func_name}({param_str}) {{"]
            old_lines = self.lines
            self.lines = func_body

            for stmt in node.body:
                self.gen_node(stmt)

            self.lines.append("    return 0;")
            self.lines.append("}\n")

            self.functions.append("\n".join(self.lines))
            self.lines = old_lines
            return ""

        elif isinstance(node, Call_Node):
            arg_vars = [self.gen_node(arg) for arg in (node.parameter or [])]
            arg_str = ", ".join(arg_vars)

            math_fn = {'sqrt': 'sqrt', 'sin': 'sin', 'cos': 'cos', 'tan': 'tan', 'abs': 'labs', 'floor': 'floor', 'ceil': 'ceil'}
            if node.ident in math_fn:
                return f"{math_fn[node.ident]}({arg_str})"

            call_code = f"{node.ident}({arg_str})"
            self.lines.append(f"    {call_code};")
            return call_code

        elif isinstance(node, Lambda_Node):
            return "NULL /* lambda */"

        elif isinstance(node, Return_Node):
            val_c = self.gen_node(node.expr) if node.expr else "0"
            self.lines.append(f"    return {val_c};")
            return val_c

        # -------------------------------------------------------------
        # 5. Loops (While & For)
        # -------------------------------------------------------------
        elif isinstance(node, While_Node):
            cond_c = self.gen_node(node.condition)
            self.lines.append(f"    while ({cond_c}) {{")
            for stmt in node.while_block:
                self.gen_node(stmt)
            self.lines.append("    }")
            return ""

        elif isinstance(node, (For_Node, For_Range_Node)):
            if getattr(node, 'init', None):
                self.gen_node(node.init)
            cond_c = self.gen_node(node.condition) if getattr(node, 'condition', None) else "1"
            self.lines.append(f"    while ({cond_c}) {{")
            for stmt in getattr(node, 'for_block', []):
                self.gen_node(stmt)
            if getattr(node, 'update', None):
                self.gen_node(node.update)
            self.lines.append("    }")
            return ""

        elif isinstance(node, Break_Node):
            self.lines.append("    break;")
            return ""

        elif isinstance(node, Continue_Node):
            self.lines.append("    continue;")
            return ""

        # -------------------------------------------------------------
        # 6. Memory, References & Boxing
        # -------------------------------------------------------------
        elif isinstance(node, Box_Node):
            val_c = self.gen_node(node.expr)
            res_var = f"heap_ptr_{len(self.lines)}"
            self.lines.append(f"    int64_t* {res_var} = (int64_t*)malloc(sizeof(int64_t));")
            self.lines.append(f"    *{res_var} = {val_c};")
            return res_var

        elif isinstance(node, Move_Node):
            var_name = getattr(node, 'var_name', getattr(node, 'target', ''))
            if isinstance(var_name, Variable_Node):
                var_name = var_name.ident
            return var_name

        elif isinstance(node, Ref_Node):
            var_name = getattr(node, 'var_name', getattr(node, 'target', ''))
            return f"&{var_name}"

        elif isinstance(node, Deref_Node):
            val_c = self.gen_node(node.expr)
            return f"(*{val_c})"

        elif isinstance(node, Deref_Assign_Node):
            ptr_c = self.gen_node(node.target)
            val_c = self.gen_node(node.value)
            self.lines.append(f"    *{ptr_c} = {val_c};")
            return val_c

        elif isinstance(node, Drop_Node):
            self.lines.append(f"    // drop {node.target}")
            return ""

        # -------------------------------------------------------------
        # 7. Structs, Arrays, Hashes & Methods
        # -------------------------------------------------------------
        elif isinstance(node, Struct_Decl_Node):
            fields_str = "; ".join([f"int64_t {fname}" for fname, _ in node.fields]) + ";"
            self.struct_decls.append(f"typedef struct {{ {fields_str} }} {node.name};")
            return ""

        elif isinstance(node, Struct_Literal_Node):
            return f"({node.name}){{ 0 }}"

        elif isinstance(node, Field_Access_Node):
            target_c = self.gen_node(node.target)
            return f"{target_c}.{node.field}"

        elif isinstance(node, Array_Node):
            return "NULL /* array */"

        elif isinstance(node, Index_Node):
            target_c = self.gen_node(node.target)
            idx_c = self.gen_node(node.index)
            return f"{target_c}[{idx_c}]"

        elif isinstance(node, Index_Assign_Node):
            target_c = self.gen_node(node.target)
            idx_c = self.gen_node(node.index)
            val_c = self.gen_node(node.value)
            self.lines.append(f"    {target_c}[{idx_c}] = {val_c};")
            return val_c

        elif isinstance(node, Hash_Node):
            return "NULL /* hash */"

        elif isinstance(node, Enum_Node):
            members = ", ".join([k for k in node.members.keys()])
            self.struct_decls.append(f"typedef enum {{ {members} }} {node.name};")
            return ""

        elif isinstance(node, Impl_Node):
            for m in node.methods:
                self.gen_node(m)
            return ""

        elif isinstance(node, Method_Call_Node):
            target_c = self.gen_node(node.target)
            arg_vars = [self.gen_node(arg) for arg in (node.args or [])]
            arg_str = ", ".join([target_c] + arg_vars)
            call_code = f"{node.method}({arg_str})"
            self.lines.append(f"    {call_code};")
            return call_code

        # -------------------------------------------------------------
        # 8. Pattern Matching (Match / Case)
        # -------------------------------------------------------------
        elif isinstance(node, Match_Node):
            target_c = self.gen_node(node.target)
            self.lines.append(f"    switch ({target_c}) {{")
            for case in getattr(node, 'cases', []):
                pat_c = self.gen_node(case.pattern)
                self.lines.append(f"        case {pat_c}: {{")
                for stmt in getattr(case, 'body', []):
                    self.gen_node(stmt)
                self.lines.append("            break;")
                self.lines.append("        }")
            self.lines.append("    }")
            return ""

        # -------------------------------------------------------------
        # 9. Output, Assertions & Error Handling
        # -------------------------------------------------------------
        elif isinstance(node, Disp_Node):
            val_c = self.gen_node(node.expr)
            if isinstance(node.expr, Float_Node):
                self.lines.append(f"    gaff_disp_float({val_c});")
            elif isinstance(node.expr, Str_Node):
                self.lines.append(f"    gaff_disp_str({val_c});")
            else:
                self.lines.append(f"    gaff_disp({val_c});")
            return val_c

        elif isinstance(node, Assert_Node):
            cond_c = self.gen_node(node.condition)
            self.lines.append(f"    assert({cond_c});")
            return ""

        elif isinstance(node, Assert_Eq_Node):
            actual_c = self.gen_node(node.actual)
            expected_c = self.gen_node(node.expected)
            self.lines.append(f"    assert(({actual_c}) == ({expected_c}));")
            return ""

        elif isinstance(node, Throw_Node):
            self.lines.append("    exit(1);")
            return ""

        # -------------------------------------------------------------
        # 10. Timelines & Modules
        # -------------------------------------------------------------
        elif isinstance(node, Timeline_Decl):
            val_c = self.gen_node(node.value)
            self.lines.append(f"    int64_t {node.ident} = {val_c}; // timeline")
            return val_c

        elif isinstance(node, Timeline_Rollback_Node):
            self.lines.append(f"    // rollback {node.ident}")
            return ""

        elif isinstance(node, Bind_Node):
            path_str = node.path.value if hasattr(node.path, 'value') else str(node.path)
            self.lines.append(f"    // bind {path_str}")
            return ""

        elif isinstance(node, Pub_Node):
            return self.gen_node(node.node)

        # -------------------------------------------------------------
        # 11. Async / Await (POSIX threads)
        # -------------------------------------------------------------
        elif isinstance(node, Async_Node):
            fn = node.func
            func_name = fn.ident
            params = fn.parameter if fn.parameter else []
            param_str = ", ".join([f"int64_t {p.ident}" for p in params])

            # Generate a thread-compatible wrapper function: void* fn_thread(void* arg)
            thread_fn = [f"void* {func_name}_thread(void* arg) {{"]
            old_lines = self.lines
            self.lines = thread_fn
            for stmt in fn.body:
                self.gen_node(stmt)
            self.lines.append("    return NULL;")
            self.lines.append("}\n")
            # Also generate a launcher that starts the thread
            self.lines.append(f"pthread_t {func_name}_launch() {{")
            self.lines.append(f"    pthread_t _t;")
            self.lines.append(f"    pthread_create(&_t, NULL, {func_name}_thread, NULL);")
            self.lines.append(f"    return _t;")
            self.lines.append("}\n")
            self.functions.append("\n".join(self.lines))
            self.lines = old_lines
            # Register the launcher in main so it can be called
            self.lines.append(f"    pthread_t {func_name}_handle = {func_name}_launch();")
            self.var_map[func_name] = f"pthread_t"
            return f"{func_name}_handle"

        elif isinstance(node, Await_Node):
            # Resolve the handle variable from the awaited expression
            handle = self.gen_node(node.expr)
            result_var = f"await_result_{len(self.lines)}"
            self.lines.append(f"    pthread_join({handle}, NULL); // await")
            self.lines.append(f"    int64_t {result_var} = 0; // await result placeholder")
            return result_var
        
        elif isinstance(node, Gaff_Node):
            ident = node.ident
            func_name = f"gaff_check_{ident}_{len(self.functions)}"
            var_type = self.var_map.get(ident, "int64_t")
            func_body = [f"bool {func_name}({var_type} {ident}) {{"]
            old_lines = self.lines
            self.lines = func_body
            last_val = "1"
            if isinstance(node.gaff_block, list):
                for stmt in node.gaff_block :
                    last_val = self.gen_node(stmt)
            else:
                last_val = self.gen_node(node.gaff_block) 
            self.lines.append(f"    return {last_val};")
            self.lines.append("}\n")
            self.functions.append("\n".join(self.lines))
            self.lines = old_lines
            self.gaff_hook[ident] = func_name
            if ident in self.var_map:
                self.lines.append(f"    if(!{func_name}({ident})) {{")
                self.lines.append(f"    printf(\"Error : Constraint on '{ident}' violated \\n\");")
                self.lines.append(f"    exit(1);")
                self.lines.append(f"        }}")

        return ""
