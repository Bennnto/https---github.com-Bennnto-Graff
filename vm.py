from opcodes import Opcode
from environment import Environment
from eval import (RuntimeArray, RuntimeHash, RuntimeEnum, VelnException,
    HeapPointer, RefPointer, heap_store, heap_next_addr)
from memory_visualizer import MemoryVisualizer
import re

class Frame:
    """Execution Frame for Function Calls"""
    def __init__(self, return_ip, local_env, instructions):
        self.return_ip = return_ip
        self.local_env = local_env
        self.instructions = instructions

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
                    
            # Arithmetic Operators
            elif op == Opcode.OP_ADD:
                b, a = self.pop(), self.pop()
                self.push(a + b)
                
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
                    call_env = Environment(parent=self.env)
                    for param, val in zip(fn_data['params'], args):
                        call_env.set(param, val)
                        
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
                else:
                    method = getattr(target, method_name)
                    self.push(method(*m_args))
                