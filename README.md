# Gaff Programming Language

[![Release Gaff Native Compiler Executables](https://github.com/Bennnto/https---github.com-Bennnto-Graff/actions/workflows/release.yml/badge.svg)](https://github.com/Bennnto/https---github.com-Bennnto-Graff/actions/workflows/release.yml)

Gaff is a statically-typed, compiled programming language featuring explicit memory safety, time-travel state debugging, constraint-based variable validation, and native C code generation.

---

## Overview

Gaff combines high-level syntax expressiveness with low-level runtime control. The language compiles directly into clean C source code using its native code generator (`NativeCodegen`), which is subsequently compiled into standalone native binary executables using system C compilers (`clang` or `gcc` with `-O3` optimizations).

---

## Architecture & Execution Pipeline

The compilation process in Gaff follows a multi-pass pipeline:

1. **Lexical Analysis (`src/lexicals.py`)**: Converts Gaff source text (`.gf` / `.gaff`) into typed tokens, keywords, and literals.
2. **LALR Parsing & AST Construction (`src/parse.py`)**: Uses PLY LALR parsing to construct an Abstract Syntax Tree (AST).
3. **Type Inference & Scope Symbol Table (`src/semantics.py`)**: Performs static type resolution and populates hierarchical scope symbol tables.
4. **Static Borrow Checker (`src/semantics.py`)**: Validates memory ownership, move semantics, and reference lifetimes to prevent dangling pointers.
5. **Scope Auto-Drop Pass (`src/semantics.py`)**: Automatically inserts memory cleanup operations at scope boundaries.
6. **Native C Code Generation (`src/native_codegen.py`)**: Translates validated AST nodes into optimized standard C code (`dist/<name>.c`).
7. **Native Binary Compilation**: Invokes `clang -O3` or `gcc -O3` to build a standalone native executable (`dist/<name>`).

---

## Core Language Systems

### 1. Memory Ownership & Lifetime Management
Gaff enforces explicit memory safety rules:
- **`box<T>`**: Heap-allocated managed pointer.
- **`ref<T>`**: Borrowed reference to a boxed or stack value.
- **`deref(r)`**: Dereferences a borrowed reference.
- **`move(b)`**: Explicitly transfers ownership to another variable binding.
- **Scope Auto-Drop**: Automatically inserts cleanup code when a variable goes out of scope.

### 2. Time-Travel Debugging (`timeline`)
Variables declared with the `timeline` modifier maintain an append-only version history of all mutations:
- **History Access**: Access prior versions using index notation (`x[0]` returns version 0).
- **State Rollback**: Roll back current variable state to a previous version index using `rollback x to 0`.

### 3. Constraint-Based State Validation (`gaff`)
Attach declarative validation constraints directly to variable bindings:
```gaff
gaff age: int {
    age >= 0
}
```
If an assignment violates the constraint block, a runtime exception is raised immediately.

### 4. Resilient Error Handling & Retry Mechanism
Gaff provides structured error propagation and automatic expression fallback capabilities:
- **`try` / `ok?`**: Try blocks with success validation.
- **`attempt(expr) fallback: { ... }`**: Evaluate an expression and execute fallback code if an exception occurs.

### 5. Memory Visualizer Tool
Inspect live stack frames, heap allocations, and reference pointers in real time using the built-in memory visualizer utility (`src/memory_visualizer.py`).

---

## Project Directory Layout

```text
.
├── src/                    # Core compiler, parser, VM, semantics, and codegen
│   ├── native_codegen.py   # Native C code generator module
│   ├── parse.py            # LALR parser and AST node definitions
│   ├── lexicals.py         # Lexer tokens and keyword definitions
│   ├── semantics.py        # Symbol table, type inferrer, and borrow checker
│   ├── eval.py             # AST evaluator engine
│   ├── vm.py               # Virtual machine and bytecode execution engine
│   ├── memory_visualizer.py# Stack and heap memory visualization utility
│   ├── builder.py          # AST node builder helper
│   ├── opcodes.py          # Bytecode instruction definitions
│   └── std_lib.py          # Standard library module implementations
├── cli/                    # CLI driver, REPL, and error reporter
│   ├── main.py             # Main CLI runner entrypoint
│   ├── repl.py             # Interactive REPL shell
│   ├── manifest.py         # Project manifest loader
│   └── error_reporter.py   # Formatted error reporter with code context
├── Test/                   # Unit and integration test suite (30+ test suites)
├── docs/                   # Documentation site configuration and guides
├── addons/                 # Extension adapters (jitto_adapter.py)
├── editors/                # Neovim and VSCode syntax highlighting packages
├── .github/workflows/      # GitHub Actions CI/CD release workflow
├── gaff                    # Executable binary runner driver
└── README.md               # Project documentation
```

---

## Pre-compiled Executables

Pre-compiled standalone executables built via PyInstaller and Native Codegen are available on [GitHub Releases](https://github.com/Bennnto/https---github.com-Bennnto-Graff/releases):

- **Windows**: `gaff-windows.exe`
- **Linux**: `gaff-linux`
- **macOS**: `gaff-macos`

---

## Installation & Quickstart Guide

### 1. Compile & Execute Immediately
Compile a `.gf` script directly to a native release binary and run it immediately:
```bash
./gaff -r main.gf
```

### 2. Build Standalone Native Executable
Compile a `.gf` file into a native executable binary saved to `dist/`:
```bash
./gaff -o my_app main.gf
./dist/my_app
```

### 3. Emit Generated C Code
Emit generated Native C source code to stdout:
```bash
./gaff --emit-c main.gf
```

### 4. Interactive REPL
Launch the interactive Gaff REPL shell:
```bash
./gaff
```

### 5. Run Test Suite
Execute the full unit and integration test suite:
```bash
for f in Test/test_*.py; do PYTHONPATH=src:cli:. python3 "$f"; done
```

---

## Language Syntax Reference

### Variables & Primitives
* primitives type variable
  * Signed Integer : i8, i16, i32, i64
  * Unsigned Integer : u8, u16, u32, u64
  * Floating Point : f32, f64
  * Size int : isize, usize, 
  * Bool : true, false
  * Char : 'a', 'b' ...
  * String : "String"
  * Fixed Size String : str[N]
  * Unit(void) 
```gaff
let x: int = 42;
let name: str = "Gaff";
let pi: float = 3.14159;
let is_valid: bool = true;
```

### Structs & Implementation Blocks
```gaff
struct Point {
    x: int,
    y: int
}

impl Point {
    fn sum(self) -> int {
        return self.x + self.y;
    }
}
```

### Pattern Matching (`match` / `case`)
```gaff
let val: int = 2;
match val {
    case 1: { print("One"); },
    case 2: { print("Two"); },
    case _: { print("Other"); }
}
```

### Time-Travel History & Rollback
```gaff
timeline count: int = 10;
count = 20;
count = 30;

// Rollback count to initial state (version index 0)
rollback count to 0;
```

### Memory Ownership (`box`, `ref`, `deref`)
```gaff
let b: box<int> = box(100);
let r: ref<int> = ref(b);
let value: int = deref(r);
```

### Fallback Error Retry (`attempt` / `fallback`)
```gaff
attempt (divide(10, 0)) fallback: {
    print("Fallback executed on divide by zero!");
};
```

### Standard Library Modules
```gaff
bind "std::math"::*;

let val: float = sqrt(25.0);
```

---

## Editor Support

- **Neovim**: Extension located at [`editors/nvim/`](file:///Users/ben/40%20Learning/41%20Code/41.01%20python/interpret/new_eval/editors/nvim)
- **VSCode**: Extension located at [`editors/vscode/`](file:///Users/ben/40%20Learning/41%20Code/41.01%20python/interpret/new_eval/editors/vscode)

---

## License

MIT License. Developed with Python and Native C Codegen.
