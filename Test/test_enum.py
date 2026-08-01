import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexicals import lexer
from parse import parser
from eval import eval_ast, Environment
from semantics import SymbolTable, Type_Infer

def test_case(code, var_name, expected_val):
    ast = parser.parse(code, lexer=lexer)
    symtab = SymbolTable()
    inferrer = Type_Infer(symtab)
    inferrer.infer_program(ast)
    env = Environment()
    for stmt in ast:
        eval_ast(stmt, env)
    
    if var_name is not None:
        actual_val = env.get(var_name)
        val = actual_val.data if hasattr(actual_val, 'data') else actual_val
        assert val == expected_val, f"Failed for {var_name}: expected {expected_val}, got {val}"
    print(f"Passed : '{var_name}' == {expected_val}")

if __name__ == "__main__":
    print("--- Running Basic Enum Tests ---")
    test_case("""
    enum Status: PENDING APPROVED REJECTED
    let p = Status.PENDING;
    let a = Status.APPROVED;
    """, "a", 1)

    test_case("""
    enum Color: RED = 10 GREEN = 20 BLUE = 30
    let c = Color.GREEN;
    """, "c", 20)

    test_case("""
    enum Priority: LOW = 5 MEDIUM HIGH = 100
    let m = Priority.MEDIUM;
    """, "m", 6)

    print("\n--- Running Real-World Use Case Tests ---")

    # Real-World Scenario 1: HTTP API Status Code Handling
    test_case("""
    enum HttpStatus: OK = 200 CREATED = 201 BAD_REQUEST = 400 UNAUTHORIZED = 401 NOT_FOUND = 404 SERVER_ERROR = 500
    
    fn is_success: bool [code: int]: {
        return (code == HttpStatus.OK) | (code == HttpStatus.CREATED);
    }

    let res1 = is_success(HttpStatus.OK);
    """, "res1", True)

    test_case("""
    enum HttpStatus: OK = 200 CREATED = 201 BAD_REQUEST = 400 UNAUTHORIZED = 401 NOT_FOUND = 404 SERVER_ERROR = 500
    
    fn is_success: bool [code: int]: {
        return (code == HttpStatus.OK) | (code == HttpStatus.CREATED);
    }

    let res2 = is_success(HttpStatus.NOT_FOUND);
    """, "res2", False)

    # Real-World Scenario 2: Role-Based Access Control (RBAC)
    test_case("""
    enum UserRole: GUEST = 0 MEMBER = 1 MODERATOR = 2 ADMIN = 3
    
    fn can_moderate: bool [role: int]: {
        return role >= UserRole.MODERATOR;
    }

    let admin_can = can_moderate(UserRole.ADMIN);
    """, "admin_can", True)

    test_case("""
    enum UserRole: GUEST = 0 MEMBER = 1 MODERATOR = 2 ADMIN = 3
    
    fn can_moderate: bool [role: int]: {
        return role >= UserRole.MODERATOR;
    }

    let guest_can = can_moderate(UserRole.GUEST);
    """, "guest_can", False)

    # Real-World Scenario 3: E-commerce Order State Machine
    test_case("""
    enum OrderState: DRAFT = 1 PLACED = 2 SHIPPED = 3 DELIVERED = 4 CANCELLED = 99

    fn next_state: int [current: int]: {
        return current == OrderState.DRAFT ? OrderState.PLACED : (current == OrderState.PLACED ? OrderState.SHIPPED : OrderState.DELIVERED);
    }

    let state_after_placed = next_state(OrderState.PLACED);
    """, "state_after_placed", 3)

    print("\nAll Real-World Enum Tests Passed Successfully!")
