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
        self.symtab = {}      # Maps variable name -> LLVM Stack pointer (e.g. 'x' -> '%x')
        self.str_counter = 0
        self.str_decls = []

    def new_reg(self):
        """Generate a unique SSA virtual register name"""
        self.reg_counter += 1
        return f"%{self.reg_counter}"

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
        self.output = []

        # 1. Generate body instructions first so string constants get populated!
        body_lines = []
        old_output = self.output
        self.output = body_lines
        for stmt in ast:
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

        # 4. Main function
        self.output.append('define i32 @main() {')
        self.output.append('entry:')

        # 5. Body instructions
        self.output.extend(body_lines)

        # 6. Footer
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
            op_map = {
                '+': 'add',
                '-': 'sub',
                '*': 'mul',
                '/': 'sdiv'
            }
            op = op_map[node.ops]
            reg = self.new_reg()
            self.output.append(f"    {reg} = {op} i64 {left_reg}, {right_reg}")
            return reg

        elif isinstance(node, Disp_Node):
            val = self.gen(node.expr)
            fmt_reg = self.new_reg()
            # If displaying a string, use %s format string, otherwise %ld
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
