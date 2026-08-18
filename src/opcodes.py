from enum import Enum, auto

class Opcode(Enum):
    OP_POP = auto()             # pop variable or operator from stack
    OP_NAME = auto()
    OP_CONST = auto()
    OP_LOAD_CONST = auto()      
    OP_LOAD_NAME = auto()       # load variable name from stack
    OP_STORE_CONST = auto()     # store variable value and name in stack
    OP_FIX = auto()             # fix variable

    # Arithmetic 
    OP_ADD = auto()
    OP_SUB = auto()
    OP_MUL = auto()
    OP_DIV = auto()
    OP_MOD = auto()
    OP_POW = auto()
    OP_NEG = auto()

    # Logical & Bitwise
    OP_AND = auto()
    OP_OR = auto()
    OP_NOT = auto()
    OP_LSHIFT = auto()
    OP_RSHIFT = auto()
    OP_BITXOR = auto()
    OP_BITNOT = auto()
    OP_FORMAT_VAL = auto()
    OP_SLICE = auto()

    # Comparison
    OP_EQ = auto()
    OP_NE = auto()
    OP_LT = auto()
    OP_GT = auto()
    OP_LE = auto()
    OP_GE = auto()
    
    # Control flow
    OP_JUMP = auto()
    OP_JUMP_IF_FALSE = auto()
    OP_JUMP_IF_TRUE = auto()
    
    # Function
    OP_MAKE_FUNC = auto()
    OP_CALL = auto()
    OP_RETURN = auto()

    # List Collection
    OP_BUILD_HASH = auto()
    OP_BUILD_ARRAY = auto()
    OP_BUILD_ENUM = auto()
    OP_BUILD_STRUCT = auto()
    OP_BINARY_INDEX = auto()
    OP_STORE_INDEX = auto()
    OP_CALL_METHOD = auto()
    OP_GET_FIELD = auto()
    

    # I/O
    OP_DISP = auto()
    OP_ENTRY = auto()

    # Timeline 
    OP_TIMELINE_DECL = auto()
    OP_TIMELINE_INDEX = auto()
    OP_ROLLBACK = auto()

    # Error Handling 
    OP_TRY = auto()
    OP_END_TRY = auto()
    OP_THROW = auto()
    OP_PUSH_OK_RESULT = auto()

    # Memory & References
    OP_BOX = auto()
    OP_MOVE = auto()
    OP_REF = auto()
    OP_DEREF = auto()
    OP_DEREF_ASSIGN = auto()

    # Interpolation
    OP_FSTR_EVAL = auto()
    OP_TO_STR = auto()

    # Others
    OP_ASSERT = auto()
    OP_FALSE = auto()
    OP_HALT = auto() 

    OP_PUB = auto()
    OP_BIND = auto()
    
    # Range & For Range
    OP_RANGE = auto()
    OP_ITER_NEW = auto()
    OP_ITER_DONE = auto()
    OP_ITER_NEXT = auto()
    
    # MATCH
    OP_DUP = auto()

    # Drop
    OP_DROP = auto()            # Drop variable and free heap memory

    # Async / Await
    OP_MAKE_ASYNC_FUNC = auto() # like OP_MAKE_FUNC but marks function as async
    OP_AWAIT = auto()           # wait for an async future result

    # Gaff Constraints
    OP_GAFF_CONSTRAINT = auto()
    