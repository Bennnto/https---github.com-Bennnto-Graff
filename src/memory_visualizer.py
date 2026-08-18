"""
Super-Compact Vertical Stack & Heap Tower Visualizer for Veln VM
"""
from eval import RuntimeArray, RuntimeHash, RuntimeEnum, HeapPointer, RefPointer

class MemoryVisualizer:
    def __init__(self):
        self.stack_base = 0x7FFF0000
        self.heap_base = 0x1000

    def visualize_step(self, step: int, ip: int, inst, stack: list, env, frames: list, heap_store: dict = None):
        width = 40
        print(f"\nSTEP {step:03d} | IP: {ip:03d} | Instruction: {inst}")

        # 1. Collect Heap Objects
        heap_objects = {}
        if heap_store:
            for addr, val in heap_store.items():
                heap_objects[addr] = val

        addr_counter = self.heap_base
        object_to_addr = {}

        def get_or_assign_heap_addr(obj):
            nonlocal addr_counter
            if isinstance(obj, HeapPointer):
                return obj.address
            if isinstance(obj, (str, RuntimeArray, RuntimeHash, RuntimeEnum)):
                if id(obj) not in object_to_addr:
                    addr = addr_counter
                    object_to_addr[id(obj)] = addr
                    heap_objects[addr] = obj
                    addr_counter += 0x20
                return object_to_addr[id(obj)]
            return None

        # Collect Evaluation Stack (Top first)
        op_stack_items = []
        curr_addr = self.stack_base

        if stack:
            for i in reversed(range(len(stack))):
                item = stack[i]
                heap_addr = get_or_assign_heap_addr(item)
                if heap_addr is not None:
                    val_str = f"0x{heap_addr:04X}"
                    type_str = "Ref"
                else:
                    val_str = str(item)
                    type_str = type(item).__name__
                op_stack_items.append((curr_addr, f"[Slot {i}]", val_str, type_str))
                curr_addr -= 4

        # Collect Scope Variables (Bottom)
        var_items = []
        if env and hasattr(env, 'bindings') and env.bindings:
            for var_name, var_val in env.bindings.items():
                heap_addr = get_or_assign_heap_addr(var_val)
                if heap_addr is not None:
                    val_str = f"0x{heap_addr:04X}"
                    type_str = "Ref"
                else:
                    val_str = str(var_val)
                    type_str = type(var_val).__name__
                var_items.append((curr_addr, var_name, val_str, type_str))
                curr_addr -= 4

        # Render Header
        print("\n      ^ STACK TOP (Last Pushed)")
        print(" ╔" + "═" * (width - 2) + "╗")

        total_rendered = 0

        # Render Evaluation Stack Slots
        if op_stack_items:
            for idx, (addr, slot_name, val_str, type_name) in enumerate(op_stack_items):
                tag = " <-- [TOP]" if idx == 0 else ""
                content = f"0x{addr:08X} | {slot_name:<8} : {val_str:<8} ({type_name})"
                print(f" ║ {content:<35} ║{tag}")
                total_rendered += 1
                if idx < len(op_stack_items) - 1:
                    print(" ╠" + "─" * (width - 2) + "╣")

        if op_stack_items and var_items:
            print(" ╠" + "═" * (width - 2) + "╣")

        # Render Scope Variables
        if var_items:
            for idx, (addr, var_name, val_str, type_name) in enumerate(var_items):
                content = f"0x{addr:08X} | {var_name:<8} : {val_str:<8} ({type_name})"
                print(f" ║ {content:<35} ║")
                total_rendered += 1

        if total_rendered == 0:
            print(f" ║ 0x{self.stack_base:08X} | [STACK EMPTY]             ║")

        print(" ╚" + "═" * (width - 2) + "╝")
        print("      v STACK BOTTOM\n")

        # Render Heap Memory Blocks below Stack
        if heap_objects:
            print("          ║ (Heap Pointer)")
            print("          v\n")
            for addr, obj in sorted(heap_objects.items()):
                if isinstance(obj, str):
                    content = f'"{obj}"'
                    meta = f"str ({len(obj)} chars)"
                elif isinstance(obj, RuntimeArray):
                    content = f"[{', '.join(map(str, obj.elements))}]"
                    meta = f"RuntimeArray ({len(obj.elements)} items)"
                elif isinstance(obj, RuntimeHash):
                    content = f"{{{', '.join(f'{k}:{v}' for k,v in obj.data.items())}}}"
                    meta = f"RuntimeHash ({len(obj.data)} keys)"
                elif isinstance(obj, RuntimeEnum):
                    content = f"Enum({obj.name})"
                    meta = f"RuntimeEnum"
                else:
                    content = str(obj)
                    meta = type(obj).__name__

                print(" ╔" + "═" * (width) + "╗")
                print(f" ║ [HEAP 0x{addr:04X}] {meta:<20} ║")
                print(f" ║ Data : {content:<35} ║")
                print(" ╚" + "═" * (width) + "╝")
