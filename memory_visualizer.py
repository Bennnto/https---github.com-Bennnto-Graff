"""
Real Stack and Heap Memory Visualizer for Veln VM
"""
from eval import RuntimeArray, RuntimeHash, RuntimeEnum, HeapPointer, RefPointer

class MemoryVisualizer:
    def __init__(self):
        # Stack starts at High Memory Address and decreases (grows downward ↓)
        self.stack_base = 0x7FFF0000
        # Heap starts at Low Memory Address and increases (grows upward ↑)
        self.heap_base = 0x1000

    def visualize_step(self, step: int, ip: int, inst, stack: list, env, frames: list, heap_store: dict = None):
        print("\n" + "=" * 95)
        print(f" 📍 STEP {step:03d} | IP: {ip:03d} | Instruction: {inst}")
        print("=" * 95)

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
            if isinstance(obj, (RuntimeArray, RuntimeHash, RuntimeEnum)):
                if id(obj) not in object_to_addr:
                    addr = addr_counter
                    object_to_addr[id(obj)] = addr
                    heap_objects[addr] = obj
                    addr_counter += 0x20
                return object_to_addr[id(obj)]
            return None

        # Scan stack & env for heap items
        for item in stack:
            get_or_assign_heap_addr(item)
        if env and hasattr(env, 'bindings'):
            for k, v in env.bindings.items():
                get_or_assign_heap_addr(v)

        # 2. Render Stack Memory
        print(" ─── 🥞 STACK MEMORY (High Address: 0x7FFF0000 ↓) ─────────────────────────────────")
        print(f"  {'ADDRESS':<12} | {'SLOT / VARIABLE':<22} | {'VALUE / CONTENT':<28} | {'TYPE':<15}")
        print(" " + "─" * 93)

        curr_addr = self.stack_base

        # Render Call Frames
        if frames:
            for i, f in enumerate(frames):
                print(f"  0x{curr_addr:08X}   | [FRAME {i}: CallFrame]      | ret_ip: {f.return_ip:03d}                       | Call Frame")
                curr_addr -= 4

        # Render Scope Environment Variables
        if env and hasattr(env, 'bindings') and env.bindings:
            for var_name, var_val in env.bindings.items():
                heap_addr = get_or_assign_heap_addr(var_val)
                if heap_addr is not None:
                    val_str = f"0x{heap_addr:04X} ──> Heap"
                    type_str = f"{type(var_val).__name__} (Ref)"
                else:
                    val_str = str(var_val)
                    type_str = type(var_val).__name__
                print(f"  0x{curr_addr:08X}   | {var_name:<22} | {val_str:<28} | {type_str:<15}")
                curr_addr -= 4

        # Render VM Evaluation Stack Slots
        if stack:
            for i, item in enumerate(stack):
                heap_addr = get_or_assign_heap_addr(item)
                slot_label = f"[STACK SLOT {i}]"
                if heap_addr is not None:
                    val_str = f"0x{heap_addr:04X} ──> Heap"
                    type_str = f"{type(item).__name__} (Ref)"
                else:
                    val_str = str(item)
                    type_str = type(item).__name__
                print(f"  0x{curr_addr:08X}   | {slot_label:<22} | {val_str:<28} | {type_str:<15}")
                curr_addr -= 4
        else:
            print(f"  0x{curr_addr:08X}   | [STACK EMPTY]          | -                          | -")

        # 3. Render Heap Memory
        print("\n ─── 🧊 HEAP MEMORY (Low Address: 0x00001000 ↑) ──────────────────────────────────")
        print(f"  {'ADDRESS':<12} | {'OBJECT TYPE':<22} | {'ALLOCATED CONTENT':<28} | {'METADATA':<15}")
        print(" " + "─" * 93)

        if heap_objects:
            for addr, obj in sorted(heap_objects.items()):
                if isinstance(obj, RuntimeArray):
                    content = f"[{', '.join(map(str, obj.elements))}]"
                    meta = f"{len(obj.elements)} elements"
                    t_name = "RuntimeArray"
                elif isinstance(obj, RuntimeHash):
                    content = f"{{{', '.join(f'{k}:{v}' for k,v in obj.data.items())}}}"
                    meta = f"{len(obj.data)} keys"
                    t_name = "RuntimeHash"
                elif isinstance(obj, RuntimeEnum):
                    content = f"Enum({obj.name})"
                    meta = f"{len(obj.members)} members"
                    t_name = "RuntimeEnum"
                else:
                    content = str(obj)
                    meta = "Raw Heap Data"
                    t_name = type(obj).__name__
                print(f"  0x{addr:04X}       | {t_name:<22} | {content:<28} | {meta:<15}")
        else:
            print(f"  0x{self.heap_base:04X}       | [HEAP EMPTY]           | -                          | -")

        print("=" * 95 + "\n")
