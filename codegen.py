from parse import (Assign_Node, Bool_Node, Int_Node, Type_Node, BinOps_Node, Str_Node, Variable_Node,
                   SingleOps_Node, Disp_Node, Entry_Node, While_Node, Return_Node, Function_Node,
                   Call_Node, For_Node, Float_Node, Param_Node, Array_Node, Index_Node, Index_Assign_Node,
                   Method_Call_Node, Array_Type_Node, Hash_Node, Hash_Type_Node, Throw_Node, Try_Ok_Node,
                   Assert_Node, Assert_Eq_Node, Attempt_Node, Lambda_Node, Box_Node, Move_Node, Ref_Node, Deref_Node,
                   Deref_Assign_Node, Fstr_Node, Match_Node, Case_Node)
import platform

class LLVMCodeGenerator:
    def __init__(self):
        self.output = []      # List of LLVM IR assembly lines 
        self.reg_counter = 0  # Counter for unique registers (%1, %2, etc.)
        self.label_counter = 0 # Counter for basic block labels
        self.symtab = {}      # Maps variable name -> LLVM Stack pointer (e.g. 'x' -> '%x')
        self.str_counter = 0
        self.str_decls = []

    def new_reg(self):
        """Generate a unique SSA virtual register name"""
        self.reg_counter += 1
        return f"%t{self.reg_counter}"

    def gen_target(self):
        """Dynamically detect OS and CPU architecture"""
        arch = platform.machine()
        sys_name = platform.system().lower()
        if sys_name == 'darwin':
            return f"{arch}-apple-darwin"
        elif sys_name == 'linux':
            return f"{arch}-pc-linux-gnu"
        elif sys_name == 'windows':
            return "x86_64-pc-windows-msvc"
        return "arm64-apple-darwin"

    def generate(self, ast):
        """Compile the AST into complete LLVM IR string."""
        self.str_counter = 0 
        self.str_decls = []
        self.reg_counter = 0
        self.label_counter = 0
        self.output = []

        # 1. Generate function definitions and body instructions separately!
        func_lines = []
        body_lines = []
        old_output = self.output
        for stmt in ast:
            if isinstance(stmt, Function_Node):
                self.output = func_lines
                self.gen(stmt)
            else:
                self.output = body_lines
                self.gen(stmt)
        self.output = old_output

        # 2. Header 
        self.output.append(f'target triple = "{self.gen_target()}"')
        self.output.append("declare i32 @printf(i8*, ...)")
        self.output.append('@.str.int = private unnamed_addr constant [5 x i8] c"%ld\\0A\\00", align 1')
        self.output.append('@.str.str = private unnamed_addr constant [4 x i8] c"%s\\0A\\00", align 1')
        self.output.append('')

        # 3. String constant declarations (MUST be global, outside functions!)
        for decl in self.str_decls:
            self.output.append(decl)
        self.output.append('')

        # 4. Global Function definitions
        self.output.extend(func_lines)

        # 5. Main function
        self.output.append('define i32 @main() {')
        self.output.append('entry:')

        # 6. Body instructions
        self.output.extend(body_lines)

        # 7. Footer
        self.output.append('    ret i32 0')
        self.output.append('}')
        return "\n".join(self.output)

    def new_str(self, text):
        """Create a global constant string array in LLVM IR."""
        self.str_counter += 1
        str_name = f"@.str.{self.str_counter}"
        byte_len = len(text.encode('utf-8')) + 1
        self.str_decls.append(f'{str_name} = private unnamed_addr constant [{byte_len} x i8] c"{text}\\00", align 1')
        return str_name, byte_len

    def gen(self, node):
        """Recursively generates LLVM IR instruction for an AST node."""
        # 1. Integer Literals (e.g. 10, 42)
        if isinstance(node, Int_Node):
            return str(node.value)

        elif isinstance(node, Bool_Node):
            # Convert true -> 1, false -> 0
            val_str = str(node.value).lower()
            return "1" if val_str == "true" or node.value is True else "0"

        elif isinstance(node, Str_Node):
            str_name, byte_len = self.new_str(node.value)
            reg = self.new_reg()
            self.output.append(f"    {reg} = getelementptr [{byte_len} x i8], [{byte_len} x i8]* {str_name}, i64 0, i64 0")
            return reg

        elif isinstance(node, Float_Node):
            # Emit e.g. "3.141593" or "0.015000"
            return f"{float(node.value):.6f}"
            
        elif isinstance(node, Assign_Node):
            val = self.gen(node.value)
            if node.ident not in self.symtab:
                ptr_name = f"%{node.ident}"
                self.output.append(f"    {ptr_name} = alloca i64, align 8")
                self.symtab[node.ident] = ptr_name
            # store eval value into stack memory
            self.output.append(f"    store i64 {val}, i64* {self.symtab[node.ident]}, align 8")
            return val

        elif isinstance(node, Variable_Node):
            reg = self.new_reg()
            ptr_name = self.symtab[node.ident]
            self.output.append(f"    {reg} = load i64, i64* {ptr_name}, align 8")
            return reg

        elif isinstance(node, BinOps_Node):
            left_reg = self.gen(node.left)
            right_reg = self.gen(node.right)
            if node.ops in ['==', '!=', '<', '>', '<=', '>=']:
                cmp_map = {'==': 'eq', '!=': 'ne', '<': 'slt', '>': 'sgt', '<=': 'sle', '>=': 'sge'}
                cond_reg = self.new_reg()
                self.output.append(f"    {cond_reg} = icmp {cmp_map[node.ops]} i64 {left_reg}, {right_reg}")
                res_reg = self.new_reg()
                self.output.append(f"    {res_reg} = zext i1 {cond_reg} to i64")
                return res_reg
            else:
                op_map = {'+': 'add', '-': 'sub', '*': 'mul', '/': 'sdiv'}
                op = op_map[node.ops]
                reg = self.new_reg()
                self.output.append(f"    {reg} = {op} i64 {left_reg}, {right_reg}")
                return reg

        elif isinstance(node, While_Node):
            lbl_id = self.label_counter
            self.label_counter += 1
            cond_label = f"while_cond_{lbl_id}"
            body_label = f"while_body_{lbl_id}"
            end_label = f"while_end_{lbl_id}"

            self.output.append(f"    br label %{cond_label}")
            self.output.append("")
            self.output.append(f"{cond_label}:")
            cond_val = self.gen(node.condition)
            cond_i1 = self.new_reg()
            self.output.append(f"    {cond_i1} = trunc i64 {cond_val} to i1")
            self.output.append(f"    br i1 {cond_i1}, label %{body_label}, label %{end_label}")
            self.output.append("")
            self.output.append(f"{body_label}:")
            for stmt in node.while_block:
                self.gen(stmt)
            self.output.append(f"    br label %{cond_label}")
            self.output.append("")
            self.output.append(f"{end_label}:")
            return None

        elif isinstance(node, Match_Node):
            target_val = self.gen(node.target)
            match_id = self.label_counter
            self.label_counter += 1
            end_label = f"match_end_{match_id}"
            
            for idx, case in enumerate(node.cases):
                case_body_label = f"case_body_{match_id}_{idx}"
                next_case_label = f"case_next_{match_id}_{idx}" if idx < len(node.cases) - 1 else end_label
                
                is_wildcard = isinstance(case.pattern, Variable_Node) and case.pattern.ident == '_'
                if is_wildcard:
                    self.output.append(f"    br label %{case_body_label}")
                else:
                    pat_val = self.gen(case.pattern)
                    cmp_reg = self.new_reg()
                    self.output.append(f"    {cmp_reg} = icmp eq i64 {target_val}, {pat_val}")
                    self.output.append(f"    br i1 {cmp_reg}, label %{case_body_label}, label %{next_case_label}")
                
                self.output.append("")
                self.output.append(f"{case_body_label}:")
                for stmt in case.body:
                    self.gen(stmt)
                self.output.append(f"    br label %{end_label}")
                self.output.append("")
                if not is_wildcard and idx < len(node.cases) - 1:
                    self.output.append(f"{next_case_label}:")
            
            self.output.append(f"{end_label}:")
            return None

        elif isinstance(node, Function_Node):
            func_name = f"@{node.ident}"
            param_strs = []
            param_names = []
            for p in (node.parameter or []):
                p_type = self.gen(p.type) if p.type else "i64"
                param_strs.append(f"{p_type} %{p.ident}_arg")
                param_names.append((p.ident, p_type))
            
            ret_type = self.gen(node.re_type) if node.re_type else "i64"
            self.output.append(f"define {ret_type} {func_name}({', '.join(param_strs)}) {{")
            self.output.append("entry:")
            
            for p_name, p_type in param_names:
                ptr_name = f"%{p_name}"
                self.output.append(f"    {ptr_name} = alloca {p_type}, align 8")
                self.output.append(f"    store {p_type} %{p_name}_arg, {p_type}* {ptr_name}, align 8")
                self.symtab[p_name] = ptr_name
                
            for stmt in node.body:
                self.gen(stmt)
                
            self.output.append(f"    ret {ret_type} 0")
            self.output.append("}")
            self.output.append("")
            return None

        elif isinstance(node, Return_Node):
            val = self.gen(node.expr) if node.expr else "0"
            self.output.append(f"    ret i64 {val}")
            return None

        elif isinstance(node, Call_Node):
            arg_vals = [self.gen(a) for a in (node.parameter or [])]
            arg_strs = [f"i64 {val}" for val in arg_vals]
            reg = self.new_reg()
            self.output.append(f"    {reg} = call i64 @{node.ident}({', '.join(arg_strs)})")
            return reg

        elif isinstance(node, Disp_Node):
            val = self.gen(node.expr)
            fmt_reg = self.new_reg()
            if isinstance(node.expr, Str_Node):
                self.output.append(f"    {fmt_reg} = getelementptr [4 x i8], [4 x i8]* @.str.str, i64 0, i64 0")
                self.output.append(f"    call i32 (i8*, ...) @printf(i8* {fmt_reg}, i8* {val})")
            else:
                self.output.append(f"    {fmt_reg} = getelementptr [5 x i8], [5 x i8]* @.str.int, i64 0, i64 0")
                self.output.append(f"    call i32 (i8*, ...) @printf(i8* {fmt_reg}, i64 {val})")
            return None

        elif isinstance(node, Type_Node):
            type_map = {
                'int': 'i64',
                'float': 'double',
                'str': 'i8*',
                'bool': 'i64',
                'void': 'void'
            }
            return type_map.get(node.type, 'i64')
