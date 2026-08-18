# ⚡ Gaff Programming Language

[![Release Gaff Native Compiler Executables](https://github.com/Bennnto/https---github.com-Bennnto-Graff/actions/workflows/release.yml/badge.svg)](https://github.com/Bennnto/https---github.com-Bennnto-Graff/actions/workflows/release.yml)

**Gaff** (`.gf` / `.gaff`) is a statically-typed, compiled programming language featuring memory safety, time-travel history debugging, constraint-based state validation, and native C code generation.

---

## ✨ Key Features

- 🚀 **Native C Code Generation**: Compiles Gaff code directly to high-performance C source and standalone native executable binaries via `clang`/`gcc` (`-O3`).
- 🛡️ **Memory Safety & Ownership**: Explicit ownership semantics with `box`, `ref`, `deref`, `move`, and automatic scope drop passes.
- ⏳ **Time-Travel Debugging (`timeline`)**: Track variable mutation history and roll back state seamlessly (`timeline`, `history`, `rollback`).
- 🎯 **Constraint-Based Validation (`gaff`)**: Attach real-time validation constraints to variables (`gaff x: int { x > 0 }`).
- 🩺 **Error Handling & Resilience**: Structured error handling (`try`/`ok?`, `throw`) and automatic fallback retry mechanisms (`attempt ... fallback`).
- 🎨 **Memory Visualizer**: Real-time stack and heap memory inspection tool (`src/memory_visualizer.py`).
- 🔌 **Editor Extensions**: Pre-configured syntax highlighting for **Neovim** and **VSCode**.
- 📦 **Cross-Platform Releases**: Pre-compiled standalone single-file executables for **Windows**, **Linux**, and **macOS**.

---

## 📁 Repository Layout

```text
.
├── src/                # Core compiler, parser, VM, semantics & native codegen
│   ├── native_codegen.py   # Native C code generator
│   ├── parse.py            # AST & LALR parser
│   ├── lexicals.py         # Lexer tokens & keywords
│   ├── semantics.py        # Symbol table, type inference & borrow checker
│   ├── eval.py             # AST evaluator
│   ├── vm.py               # Virtual Machine & bytecode engine
│   ├── memory_visualizer.py# Stack & Heap visualizer tool
│   └── std_lib.py          # Standard library implementations
├── cli/                # CLI driver, REPL & error reporting
│   ├── main.py             # CLI runner entrypoint
│   ├── repl.py             # Interactive REPL
│   └── error_reporter.py   # Formatted error messages with code context
├── Test/               # Comprehensive test suite (30+ test files)
├── docs/               # Documentation site configuration & guides
├── addons/             # Adapter extensions
├── editors/            # Neovim & VSCode syntax plugins
├── .github/workflows/  # GitHub Actions CI/CD & release automation
├── gaff                # Standalone native runner script executable
└── README.md           # Project documentation
```

---

## 📥 Download Standalone Executables

Pre-compiled standalone binaries generated via PyInstaller and Native Codegen are available on [GitHub Releases](https://github.com/Bennnto/https---github.com-Bennnto-Graff/releases):

- 🪟 **Windows**: `gaff-windows.exe`
- 🐧 **Linux**: `gaff-linux`
- 🍎 **macOS**: `gaff-macos`

---

## 🚀 Quickstart Guide

### 1. Compile & Execute a Gaff Script
Compile a `.gf` script directly to a native release binary and execute it immediately:
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

### 4. Launch Interactive REPL
Start the interactive Gaff REPL:
```bash
./gaff
```

### 5. Run Test Suite
Run the full test suite:
```bash
for f in Test/test_*.py; do PYTHONPATH=src:cli:. python3 "$f"; done
```

---

## 💻 Language Syntax Examples

### 1. Primitive Variables & Static Typing
```gaff
let x: int = 42;
let name: str = "Gaff";
let pi: float = 3.14159;
let is_fast: bool = true;
```

### 2. Time-Travel History (`timeline`)
```gaff
timeline score: int = 100;
score = 150;
score = 200;

// Rollback score to version 0
rollback score to 0;
```

### 3. Constraint-Based Validation (`gaff`)
```gaff
gaff age: int {
    age >= 0
}
```

### 4. Memory Ownership & References
```gaff
let b: box<int> = box(100);
let r: ref<int> = ref(b);
let val: int = deref(r);
```

### 5. Fallback Error Retry (`attempt` / `fallback`)
```gaff
attempt (divide(10, 0)) fallback: {
    print("Fallback executed on error!");
};
```

---

## 🔌 Editor Plugins

- **Neovim**: Load plugin from [`editors/nvim/`](file:///Users/ben/40%20Learning/41%20Code/41.01%20python/interpret/new_eval/editors/nvim)
- **VSCode**: Load extension from [`editors/vscode/`](file:///Users/ben/40%20Learning/41%20Code/41.01%20python/interpret/new_eval/editors/vscode)

---

## 📜 License

MIT License. Developed with Python & Native C Codegen.
