import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexicals import lexer
from parse import parser
from eval import eval_ast
from semantics import SymbolTable, Type_Infer

# ── Helpers ────────────────────────────────────────────────────────────────────

def run(code):
    """Parse, type-check, and evaluate code. Return final env dict."""
    ast = parser.parse(code, lexer=lexer)
    symtab = SymbolTable()
    inferrer = Type_Infer(symtab)
    inferrer.infer_program(ast)
    env = {}
    for stmt in ast:
        eval_ast(stmt, env)
    return env

def current(env, name):
    """Get current (latest) value of a timeline variable."""
    val = env.get(name)
    return val[-1] if isinstance(val, list) else val

def history(env, name):
    """Get the full history list of a timeline variable."""
    return env.get(name)

def check(label, actual, expected):
    assert actual == expected, f"FAILED [{label}] expected {expected!r} got {actual!r}"
    print(f"  PASSED [{label}]")

# ── Tests ──────────────────────────────────────────────────────────────────────

def test_basic_declaration():
    """let timeline x = 5 — initial value is stored as version 0."""
    env = run("let timeline x = 5")
    check("initial value", current(env, 'x'), 5)
    check("history length = 1", len(history(env, 'x')), 1)

def test_typed_declaration():
    """let timeline x : int = 10 — typed declaration works."""
    env = run("let timeline x : int = 10")
    check("typed initial value", current(env, 'x'), 10)

def test_update_appends_history():
    """Assigning to a timeline variable should append a new version."""
    env = run("""
    let timeline x = 1
    x = 2
    x = 3
    """)
    check("current value after updates", current(env, 'x'), 3)
    check("history length = 3", len(history(env, 'x')), 3)
    check("version 0", history(env, 'x')[0], 1)
    check("version 1", history(env, 'x')[1], 2)
    check("version 2", history(env, 'x')[2], 3)

def test_rollback_to_index():
    """rollback x@1 — trims history to index 1 (keeps versions 0..1)."""
    env = run("""
    let timeline x : int = 5
    x = 10
    x = 20
    x = 25
    rollback x@1
    """)
    check("current value after rollback", current(env, 'x'), 10)
    check("history trimmed to 2 versions", len(history(env, 'x')), 2)

def test_rollback_to_first_version():
    """rollback x@0 — rolls back all the way to initial value."""
    env = run("""
    let timeline x = 100
    x = 200
    x = 300
    rollback x@0
    """)
    check("current value is initial", current(env, 'x'), 100)
    check("history trimmed to 1 version", len(history(env, 'x')), 1)

def test_history_access_at_index():
    """x @ 0 — access a specific historical value as an expression."""
    env = run("""
    let timeline x = 10
    x = 20
    x = 30
    let y = x @ 0
    """)
    check("y == version 0 of x", env.get('y'), 10)

def test_history_access_latest():
    """x @ 2 — access the latest version by explicit index."""
    env = run("""
    let timeline x = 1
    x = 2
    x = 3
    let y = x @ 2
    """)
    check("y == version 2 of x", env.get('y'), 3)

def test_multiple_timelines():
    """Two independent timeline variables don't interfere."""
    env = run("""
    let timeline a = 1
    let timeline b = 100
    a = 2
    b = 200
    rollback a@0
    """)
    check("a rolled back to 1", current(env, 'a'), 1)
    check("b unaffected, still 200", current(env, 'b'), 200)

def test_timeline_with_float():
    """Timeline works with float type."""
    env = run("""
    let timeline score : float = 1.0
    score = 2.5
    score = 3.7
    rollback score@1
    """)
    check("float rollback current", current(env, 'score'), 2.5)

def test_timeline_with_string():
    """Timeline works with string values."""
    env = run("""
    let timeline msg = "hello"
    msg = "world"
    msg = "bye"
    rollback msg@0
    """)
    check("string rollback to initial", current(env, 'msg'), "hello")

# ── Runner ─────────────────────────────────────────────────────────────────────

TESTS = [
    ("Basic declaration",            test_basic_declaration),
    ("Typed declaration",            test_typed_declaration),
    ("Update appends history",       test_update_appends_history),
    ("Rollback to index",            test_rollback_to_index),
    ("Rollback to first version",    test_rollback_to_first_version),
    ("History access at index",      test_history_access_at_index),
    ("History access latest",        test_history_access_latest),
    ("Multiple timelines",           test_multiple_timelines),
    ("Timeline with float",          test_timeline_with_float),
    ("Timeline with string",         test_timeline_with_string),
]

if __name__ == "__main__":
    passed = 0
    failed = 0
    for name, fn in TESTS:
        print(f"\n▶ {name}")
        try:
            fn()
            passed += 1
        except Exception as e:
            print(f"  FAILED: {e}")
            failed += 1
    print(f"\n{'='*40}")
    print(f"Results: {passed}/{passed + failed} passed")
    if failed:
        sys.exit(1)
