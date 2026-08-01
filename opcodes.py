from enum import Enum, auto

class Opcode(Enum):
    OP_POP = auto() 
    OP_NAME = auto()
    OP_CONST = auto()
    OP_LOAD_CONST = auto()
    OP_LOAD_NAME = auto()

    # Arithmetic 
    OP_ADD = auto()
    OP_SUB = auto()
    OP_MUL = auto()
    OP_DIV = auto()
    OP_MOD = auto()
    OP_POW = auto()
    OP_NEG = auto()

    # Logical
    OP_AND = auto()
    OP_OR = auto()
    OP_NOT = auto()

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
    OP_BINARY_INDEX = auto()
    OP_STORE_INDEX = auto()
    OP_CALL_METHOD = auto()

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

    # Others
    OP_ASSERT = auto()
    OP_FALSE = auto()
    OP_HALT = auto() 