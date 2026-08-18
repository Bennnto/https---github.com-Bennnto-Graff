from Test import test_assert
from Test import test_assert
from opcodes import Opcode
from environment import Environment
from eval import (RuntimeArray, RuntimeHash, RuntimeEnum, GaffException, VelnException, RuntimeStruct,
    HeapPointer, RefPointer, heap_store, heap_next_addr)
from memory_visualizer import MemoryVisualizer
import re
import os
from compiler import Compiler
from parse import parser
from lexicals import lexer
from std_lib import STD_MODULES
import threading

class Frame:
    """Execution Frame for Function Calls"""
    def __init__(self, return_ip, local_env, instructions):
        self.return_ip = return_ip
        self.local_env = local_env
        self.instructions = instructions
        
class PeekIter:
    def __init__(self, it):
        self.it = it
        self._next = None
        self._has_next = True
        self._advance()
    
    def _advance(self):
        try:
            self._next =next(self.it)
        except StopIteration:
            self._has_next = False
            self._next = None
            
    def __next__(self):
        if not self._has_next:
            raise StopIteration
        val=self._next
        self._advance()
        return val
    
    def peek(self):
        return self._next, self._has_next
    
            
class VM:
    def __init__(self):
        self.stack = []
        self.ip = 0
        self.frames = []
        self.env = Environment()
        self.try_stack = []
        self.instructions = []
        self.visualizer = MemoryVisualizer()
        self.debug = False
        
    def push(self, val):
        self.stack.append(val)
        
    def pop(self):
        if not self.stack:
            raise RuntimeError("Error : VM Stack Underflow Error")
        return self.stack.pop()
    
    def run(self, instructions, debug=False):
        self.instructions = instructions
        self.ip = 0
        self.stack.clear()
        self.frames.clear()
        self.debug = debug
        step_count = 0
        while self.ip < len(self.instructions):
            inst = self.instructions[self.ip]
            op = inst.op
            arg = inst.arg
            curr_ip = self.ip
            self.ip += 1
            step_count += 1

            if self.debug:
                self.visualizer.visualize_step(
                    step=step_count,
                    ip=curr_ip,
                    inst=inst,
                    stack=self.stack,
                    env=self.env,
                    frames=self.frames,
                    heap_store=heap_store
                )
            
            # Cosntant and Variables
            if op in (Opcode.OP_CONST, Opcode.OP_LOAD_CONST):
                self.push(arg)
                
            elif op == Opcode.OP_LOAD_NAME:
                val = self.env.get(arg)
                self.push(val)
            
            elif op == Opcode.OP_NAME or op == getattr(Opcode, 'OP_STORE_NAME', Opcode.OP_NAME):
                val = self.pop()
                self.env.set(arg, val)
                
            elif op == Opcode.OP_POP:
                if self.stack:
                    self.pop()

            elif op == Opcode.OP_DUP:
                if not self.stack:
                    raise RuntimeError("Error : VM Stack Underflow Error")
                self.push(self.stack[-1])
                    
            # Arithmetic Operators
            elif op == Opcode.OP_ADD:
                b, a = self.pop(), self.pop()
                if isinstance(a, str) or isinstance(b, str):
                    self.push(str(a) + str(b))
                else:
                    self.push(a + b)
                    
            elif op == Opcode.OP_TO_STR:
                val = self.pop()
                self.push(str(val))

            elif op == Opcode.OP_FSTR_EVAL:
                val = self.pop()
                self.push(str(val))
                
            elif op == Opcode.OP_SUB:
                b, a = self.pop(), self.pop()
                self.push(a - b)
                
            elif op == Opcode.OP_MUL:
                b, a = self.pop(), self.pop()
                self.push(a * b)
            
            elif op == Opcode.OP_DIV:
                b, a = self.pop(), self.pop()
                if b == 0 :
                    raise ZeroDivisionError(f"Error : Divided by zero not allowed")                           
                self.push(a / b)

            elif op == Opcode.OP_MOD:
                b, a = self.pop(), self.pop()
                if b == 0 :
                    raise ZeroDivisionError(f"Error : Divided by zero not allowed") 
                self.push(a % b)
                
            elif op == Opcode.OP_POW:
                b, a = self.pop(), self.pop()
                self.push(a ** b)
                
            elif op == Opcode.OP_NEG:
                self.push(-self.pop())
            
            # Comparison and Logical Operators
            
            elif op == Opcode.OP_EQ:
                b, a = self.pop(), self.pop()
                self.push(a == b)
                
            elif op == Opcode.OP_NE:
                b, a = self.pop(), self.pop()
                self.push(a != b)
            
            elif op == Opcode.OP_LT:
                b, a = self.pop(), self.pop()
                self.push(a < b)
            
            elif op == Opcode.OP_GT:
                b, a = self.pop(), self.pop()
                self.push(a > b)
                
            elif op == Opcode.OP_LE:
                b, a = self.pop(), self.pop()
                self.push(a <= b)
                
            elif op == Opcode.OP_GE:
                b, a = self.pop(), self.pop()
                self.push(a >= b)
                
            elif op == Opcode.OP_OR:
                b, a = self.pop(), self.pop()
                self.push(a or b)
                
            elif op == Opcode.OP_AND:
                b, a = self.pop(), self.pop()
                self.push(a and b)
                
            elif op == Opcode.OP_NOT:
                self.push(not self.pop())

            elif op == Opcode.OP_LSHIFT:
                b, a = self.pop(), self.pop()
                self.push(a << b)

            elif op == Opcode.OP_RSHIFT:
                b, a = self.pop(), self.pop()
                self.push(a >> b)

            elif op == Opcode.OP_BITXOR:
                b, a = self.pop(), self.pop()
                self.push(a ^ b)

            elif op == Opcode.OP_BITNOT:
                self.push(~self.pop())

            elif op == Opcode.OP_FORMAT_VAL:
                fmt_spec = arg
                val = self.pop()
                self.push(format(val, fmt_spec))

            elif op == Opcode.OP_SLICE:
                stop = self.pop()
                start = self.pop()
                target = self.pop()
                start_idx = 0 if start is None else start
                if isinstance(target, RuntimeArray):
                    stop_idx = len(target.elements) if stop is None else stop
                    self.push(RuntimeArray(target.elements[start_idx:stop_idx]))
                elif isinstance(target, list):
                    stop_idx = len(target) if stop is None else stop
                    self.push(target[start_idx:stop_idx])
                elif isinstance(target, str):
                    stop_idx = len(target) if stop is None else stop
                    self.push(target[start_idx:stop_idx])
                else:
                    raise RuntimeError("VM Error: Target is not sliceable")
                
            # Control Flow
            elif op == Opcode.OP_JUMP:
                self.ip = arg
                
            elif op == Opcode.OP_JUMP_IF_FALSE:
                cond = self.pop()
                if not cond:
                    self.ip = arg
            
            elif op == Opcode.OP_JUMP_IF_TRUE:
                cond = self.pop()
                if cond:
                    self.ip = arg
                    
            #Functions and Calls
            elif op == Opcode.OP_MAKE_FUNC:
                self.push(arg)

            elif op == Opcode.OP_MAKE_ASYNC_FUNC:
                # Same as OP_MAKE_FUNC — the is_async flag is already inside arg dict
                self.push(arg)
            
            elif op == Opcode.OP_CALL:
                fn_name, arg_count = arg
                args = [self.pop() for _ in range(arg_count)][::-1]
                if fn_name in ['int', 'to_int']:
                    self.push(int(args[0]))
                elif fn_name in ['float', 'to_float']:
                    self.push(float(args[0]))
                elif fn_name in ['str', 'to_str']:
                    self.push(str(args[0]))
                elif fn_name == 'abs':
                    self.push(abs(args[0]))
                else :
                    fn_data = self.env.get(fn_name)
                    if callable(fn_data):
                        self.push(fn_data(*args))
                    elif isinstance(fn_data, dict):
                        call_env = Environment(parent=self.env)
                        params = fn_data['params']
                        defaults = fn_data.get('defaults', {})
                        for i, param in enumerate(params):
                            if i < len(args):
                                call_env.set(param, args[i])
                            elif param in defaults:
                                call_env.set(param, defaults[param])
                            else:
                                raise RuntimeError(f"Error: Function '{fn_name}' missing argument for '{param}'")

                        # --- Async path: run in a background thread ---
                        if fn_data.get('is_async', False):
                            result_box = {'__result__': None, '__thread__': None}
                            def run_async(code=fn_data['code'], env=call_env, box=result_box):
                                sub_vm = VM(env)
                                box['__result__'] = sub_vm.run(code)
                            t = threading.Thread(target=run_async)
                            result_box['__thread__'] = t
                            t.start()
                            self.push(result_box)   # return future immediately
                        else:
                            # --- Sync path: existing behaviour ---
                            self.frames.append(Frame(return_ip=self.ip, local_env=self.env, instructions=self.instructions))
                            self.env = call_env
                            self.instructions = fn_data['code']
                            self.ip = 0

            elif op == Opcode.OP_RETURN:
                ret_val = self.pop()
                if self.frames:
                    frame = self.frames.pop()
                    self.ip = frame.return_ip
                    self.env = frame.local_env
                    self.instructions = frame.instructions
                self.push(ret_val)
                
            # Collection and Enum
            elif op == Opcode.OP_BUILD_ARRAY :
                elements = [self.pop() for _ in range(arg)][::-1]
                self.push(RuntimeArray(elements))
                
            elif op == Opcode.OP_BUILD_HASH :
                pairs = []
                for _ in range(arg):
                    val = self.pop()
                    key = self.pop()
                    pairs.append((key, val))
                pairs.reverse()
                self.push(RuntimeHash(pairs))
                
            elif op == Opcode.OP_BUILD_ENUM:
                count = arg
                members = {}
                auto_val = 0
                raw_pairs = []
                for _ in range(count):
                    val = self.pop()
                    key = self.pop()
                    raw_pairs.append((key, val))
                raw_pairs.reverse()
                
                for name, val in raw_pairs:
                    if val is not None :
                        members[name] = val
                        if isinstance(val, int):
                            auto_val = val + 1
                    else:
                        members[name] = auto_val
                        auto_val += 1
                enum_name = self.pop()
                enum_obj = RuntimeEnum(enum_name, members)
                self.env.set(enum_name, enum_obj)
                self.push(enum_obj)

            elif op == Opcode.OP_BINARY_INDEX:
                index = self.pop()
                target = self.pop()
                if isinstance(target, RuntimeEnum):
                    self.push(target.get(index))
                elif isinstance(target, RuntimeArray):
                    self.push(target.get(index))
                elif isinstance(target, RuntimeHash):
                    self.push(target.get(index))
                else:
                    raise RuntimeError(f"Error : Invalid index target '{target}'")

            elif op == Opcode.OP_STORE_INDEX:
                val = self.pop()
                index = self.pop()
                target = self.pop()
                if isinstance(target, (RuntimeArray, RuntimeHash)):
                    target.set(index, val)
                self.push(val)

            elif op == Opcode.OP_CALL_METHOD:
                method_name, arg_count = arg
                m_args = [self.pop() for _ in range(arg_count)][::-1]
                target = self.pop()
                if isinstance(target, list) and method_name == 'history':
                    self.push(list(target))
                elif isinstance(target, RuntimeStruct) and self.env.contains(method_name):
                    fn_data = self.env.get(method_name)
                    call_env = Environment(parent=self.env)
                    call_env.set('self', target)
                    params = [p for p in fn_data['params'] if p != 'self']
                    for param, val in zip(params, m_args):
                        call_env.set(param, val)
                    self.frames.append(Frame(self.ip, self.env, self.instructions))
                    self.env = call_env
                    self.instructions = fn_data['code']
                    self.ip = 0
                elif isinstance(target, dict) and method_name in target:
                    fn = target[method_name]
                    if callable(fn):
                        self.push(fn(*m_args))
                    else:
                        self.push(fn)
                elif hasattr(target, method_name):
                    method = getattr(target, method_name)
                    if callable(method):
                        self.push(method(*m_args))
                    else:
                        self.push(method)
                else:
                    raise RuntimeError(f"Error : Target '{target}' has no method or attribute '{method_name}'")
                
            elif op == Opcode.OP_STORE_CONST:
                var_name, const_val = arg
                self.env.set(var_name, const_val)

            elif op == Opcode.OP_PUB:
                symbol_name = arg
                if symbol_name:
                    if '__export__' not in self.env:
                        self.env.set('__export__', {})
                    exports = self.env.get('__export__')
                    if self.env.contains(symbol_name):
                        exports[symbol_name] = self.env.get(symbol_name)

            elif op == Opcode.OP_BIND:
                file_path = self.pop()
                alias_name = arg

                if file_path in STD_MODULES:
                    exports = STD_MODULES[file_path]
                else:
                    if not os.path.exists(file_path):
                        raise FileNotFoundError(f"Error : File '{file_path}' not found")

                    with open(file_path, 'r', encoding='utf-8') as f:
                        code = f.read()

                    module_ast = parser.parse(code, lexer=lexer)
                    compiler = Compiler()
                    module_instructions = compiler.compile(module_ast)
                    module_vm = VM()
                    module_vm.run(module_instructions)
                    exports = module_vm.env.get('__export__', {})

                if isinstance(alias_name, list):
                    for sym in alias_name:
                        if sym in exports:
                            self.env.set(sym, exports[sym])
                        else:
                            raise RuntimeError(f"Error : Name '{sym}' not found in module '{file_path}'")
                elif alias_name == '*':
                    for k, v in exports.items():
                        self.env.set(k, v)
                else:
                    if alias_name in exports:
                        self.env.set(alias_name, exports[alias_name])
                    else:
                        self.env.set(alias_name, exports)

            elif op == Opcode.OP_RANGE:
                arg_count = arg # 1, 2, 3
                if arg_count == 1 :
                    stop = self.pop()
                    self.push(range(stop))
                elif arg_count == 2 :
                    stop = self.pop()
                    start = self.pop()
                    self.push(range(start, stop))
                elif arg_count == 3 :
                    step = self.pop()
                    stop = self.pop()
                    start = self.pop()
                    self.push(range(start, stop, step))
                    
            elif op == Opcode.OP_ITER_NEW:
                obj = self.pop()
                self.push(PeekIter(iter(obj)))
                
            elif op == Opcode.OP_ITER_NEXT:
                it = self.stack[-1]
                val = next(it)
                self.push(val)
                    
            elif op == Opcode.OP_ITER_DONE:
                it = self.stack[-1]
                _, has_next = it.peek()
                if not has_next:
                    self.stack.pop()
                    self.ip = arg
                    
            elif op == Opcode.OP_FIX:
                ident, value = arg
                if ident in self.env :
                    raise RuntimeError(f"Error : Fix variable {ident} already declared")
                self.env.set(ident, value)
                if isinstance(self.env, Environment):
                    self.env.mark_immutable(ident)

            elif op == Opcode.OP_BUILD_STRUCT:
                name, count, field_name = arg
                value = [self.pop() for _ in range(count)][::-1]
                fields =  dict(zip(field_name, value))
                self.push(RuntimeStruct(name, fields))

            elif op == Opcode.OP_GET_FIELD:
                field_name = arg
                struct_obj = self.pop()
                if isinstance(struct_obj, RuntimeStruct):
                    if field_name in struct_obj.fields:
                        self.push(struct_obj.fields[field_name])
                    else :
                        raise RuntimeError(f"Error : Field {field_name} not found in struct {struct_obj.name}")
                elif isinstance(struct_obj, RuntimeEnum):
                    self.push(struct_obj.get(field_name))
                else :
                   raise RuntimeError(f"VM Error: Target is not a struct instance, got {type(struct_obj).__name__}")
                    
            
            elif op == Opcode.OP_DROP :
                if self.env.contains(arg):
                    val = self.env.get(arg, None)
                    if isinstance(val, HeapPointer) and val.address in heap_store:
                        del heap_store[val.address]
                    if arg in self.env.bindings:
                        del self.env.bindings[arg]

            elif op == Opcode.OP_AWAIT:
                future = self.pop()
                if isinstance(future, dict) and '__thread__' in future:
                    future['__thread__'].join()        # block until the async thread finishes
                    self.push(future['__result__'])    # push the real result
                else:
                    self.push(future)                  # not async, just pass through

            elif op == Opcode.OP_GAFF_CONSTRAINT:
                target = arg['target']
                code = arg['code']
                
                def constraint_fn(new_val, current_env=self.env, code=code):
                    saved_stack = self.stack.copy()
                    saved_frames = self.frames.copy()
                    saved_ip = self.ip
                    saved_instructions = self.instructions
                    saved_env = self.env
                    
                    hook_env = Environment(parent=current_env)
                    hook_env.bindings[target] = new_val
                    
                    try:
                        self.run(code, debug=self.debug)
                        if self.stack:
                            result = self.pop()
                            if result is False:
                                raise RuntimeError(f"Error : Constraint on '{target}' violated.")
                    finally:
                        self.stack = saved_stack
                        self.frames = saved_frames
                        self.ip = saved_ip
                        self.instructions = saved_instructions
                        self.env = saved_env

                self.env.add_hook(target, constraint_fn)
                if self.env.contains(target):
                    constraint_fn(self.env.get(target))