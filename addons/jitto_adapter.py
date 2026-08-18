"""
Jitto AST Adapter & Comprehensive Normalizer for new_eval
Maps ALL AST Node types in new_eval to jitto native compilation targets with fallback.
"""

from dataclasses import is_dataclass, asdict
try:
    import jitto
    HAS_JITTO = True
except ImportError:
    HAS_JITTO = False
    jitto = None

from eval import eval_ast

class JittoASTAdapter:
    """
    Adapter that converts all new_eval AST nodes into jitto-normalizable structures.
    """

    @staticmethod
    def normalize_node(node: Any) -> Any:
        if node is None:
            return None

        if isinstance(node, list):
            return [JittoASTAdapter.normalize_node(item) for item in node]

        if isinstance(node, tuple):
            return tuple(JittoASTAdapter.normalize_node(item) for item in node)

        node_type = type(node).__name__

        # 1. Primitives & Literals
        if node_type == 'Int_Node':
            return {'type': 'Constant', 'value': node.value}

        if node_type in ('Float_Node', 'Str_Node', 'Bool_Node'):
            return {'type': 'Constant', 'value': getattr(node, 'value', None)}

        if node_type == 'Void_Node':
            return {'type': 'Constant', 'value': None}

        # 2. Variables & Identifier Lookups
        if node_type == 'Variable_Node':
            return {'type': 'Name', 'id': node.ident}

        # 3. Binary Operations (+, -, *, /, %, >, <, ==, !=, >=, <=, &, |, ^, <<, >>)
        if node_type == 'BinOps_Node':
            return {
                'type': 'BinOp',
                'op': node.ops,
                'left': JittoASTAdapter.normalize_node(node.left),
                'right': JittoASTAdapter.normalize_node(node.right)
            }

        # 4. Unary / Single Operations (-, !, ~)
        if node_type == 'SingleOps_Node':
            return {
                'type': 'UnaryOp',
                'op': node.ops,
                'right': JittoASTAdapter.normalize_node(node.right)
            }

        # 5. Assignments & Fix Declarations
        if node_type in ('Assign_Node', 'Fix_Node'):
            return {
                'type': 'Assign',
                'target': getattr(node, 'ident', ''),
                'value': JittoASTAdapter.normalize_node(getattr(node, 'value', None))
            }

        # 6. Collections (Arrays, Hashes, Slicing, Indexing)
        if node_type == 'Array_Node':
            return {
                'type': 'Array',
                'elements': [JittoASTAdapter.normalize_node(e) for e in getattr(node, 'elements', [])]
            }

        if node_type == 'Hash_Node':
            return {
                'type': 'Hash',
                'elements': [(JittoASTAdapter.normalize_node(k), JittoASTAdapter.normalize_node(v))
                             for k, v in getattr(node, 'elements', [])]
            }

        if node_type == 'Index_Node':
            return {
                'type': 'Subscript',
                'target': JittoASTAdapter.normalize_node(node.target),
                'index': JittoASTAdapter.normalize_node(node.index)
            }

        if node_type == 'Index_Assign_Node':
            return {
                'type': 'SubscriptAssign',
                'target': JittoASTAdapter.normalize_node(node.target),
                'index': JittoASTAdapter.normalize_node(node.index),
                'value': JittoASTAdapter.normalize_node(node.value)
            }

        # 7. Range & Slicing Nodes
        if node_type == 'Range_Node':
            return {
                'type': 'Range',
                'start': JittoASTAdapter.normalize_node(getattr(node, 'start', None)),
                'stop': JittoASTAdapter.normalize_node(getattr(node, 'stop', None)),
                'step': JittoASTAdapter.normalize_node(getattr(node, 'step', None)),
                'amount': JittoASTAdapter.normalize_node(getattr(node, 'amount', None))
            }

        # 8. Function Calls, Lambdas & Conditionals
        if node_type == 'Call_Node':
            return {
                'type': 'Call',
                'func': node.ident,
                'args': [JittoASTAdapter.normalize_node(arg) for arg in (node.parameter or [])]
            }

        if node_type == 'Lambda_Node':
            return {
                'type': 'Lambda',
                'params': getattr(node, 'params', []),
                'body': JittoASTAdapter.normalize_node(node.body)
            }

        if node_type == 'Ternary_Node':
            return {
                'type': 'IfExp',
                'test': JittoASTAdapter.normalize_node(node.condition),
                'body': JittoASTAdapter.normalize_node(node.true_block),
                'orelse': JittoASTAdapter.normalize_node(node.false_block)
            }

        # 9. Pattern Matching (Match / Case)
        if node_type == 'Match_Node':
            return {
                'type': 'Match',
                'subject': JittoASTAdapter.normalize_node(node.target),
                'cases': [JittoASTAdapter.normalize_node(c) for c in getattr(node, 'cases', [])]
            }

        if node_type == 'Case_Node':
            return {
                'type': 'match_case',
                'pattern': JittoASTAdapter.normalize_node(node.pattern),
                'body': JittoASTAdapter.normalize_node(node.body)
            }

        # 10. Memory, References & Ownership (Ref, Deref, Box, Move)
        if node_type == 'Ref_Node':
            return {'type': 'Reference', 'target': node.var_name, 'mutable': node.is_mutable}

        if node_type in ('Deref_Node', 'Box_Node'):
            return {'type': 'Dereference', 'value': JittoASTAdapter.normalize_node(node.expr)}

        if node_type == 'Move_Node':
            return {'type': 'Move', 'target': node.var_name}

        # 11. Timeline & Rollback
        if node_type == 'Timeline_Decl':
            return {
                'type': 'TimelineDecl',
                'target': node.ident,
                'value': JittoASTAdapter.normalize_node(node.value)
            }

        if node_type == 'Timeline_Rollback_Node':
            return {
                'type': 'TimelineRollback',
                'target': node.ident,
                'index': JittoASTAdapter.normalize_node(getattr(node, 'index', None))
            }

        # 12. Error Handling (Try_Ok, Attempt, Throw)
        if node_type == 'Try_Ok_Node':
            return {
                'type': 'TryOk',
                'try_block': JittoASTAdapter.normalize_node(node.try_block),
                'ok_block': JittoASTAdapter.normalize_node(node.ok_block)
            }

        if node_type == 'Attempt_Node':
            return {
                'type': 'Attempt',
                'attempt_block': JittoASTAdapter.normalize_node(node.attempt_block),
                'fallback_block': JittoASTAdapter.normalize_node(node.fallback_block)
            }

        if node_type == 'Throw_Node':
            return {'type': 'Throw', 'value': JittoASTAdapter.normalize_node(node.expr)}

        # 13. F-String Interpolation
        if node_type == 'Fstr_Node':
            return {
                'type': 'JoinedStr',
                'parts': [JittoASTAdapter.normalize_node(p) for p in getattr(node, 'parts', [])]
            }

        # 14. Assertions (Assert, Assert_Eq)
        if node_type == 'Assert_Node':
            return {'type': 'Assert', 'test': JittoASTAdapter.normalize_node(node.condition)}

        if node_type == 'Assert_Eq_Node':
            return {
                'type': 'AssertEq',
                'left': JittoASTAdapter.normalize_node(node.actual),
                'right': JittoASTAdapter.normalize_node(node.expected)
            }

        # 15. Enums, Structs & Generics
        if node_type == 'Enum_Node':
            return {'type': 'EnumDecl', 'name': node.name, 'members': node.members}

        if node_type == 'Generic_Type_Node':
            return {'type': 'GenericType', 'name': node.name, 'args': node.type_args}

        # Fallback: Convert dataclass node to generic dict AST
        if is_dataclass(node):
            node_dict = {'type': node_type}
            for k, v in asdict(node).items():
                node_dict[k] = JittoASTAdapter.normalize_node(v)
            return node_dict

        return node

    @staticmethod
    def execute(node: Any, env: Any) -> Any:
        """
        Executes any new_eval AST node natively through jitto when possible,
        falling back to eval_ast for dynamic interpreter features.
        """
        if node is None:
            return None

        if isinstance(node, list):
            last_res = None
            for item in node:
                last_res = JittoASTAdapter.execute(item, env)
            return last_res

        # Retrieve environment bindings dictionary
        env_dict = env.bindings if hasattr(env, 'bindings') else env

        if HAS_JITTO and jitto is not None:
            try:
                # 1. Normalize new_eval AST node to jitto-compatible AST structure
                normalized = JittoASTAdapter.normalize_node(node)
                # 2. Run Native Machine Code Execution via jitto
                return jitto.run_jit(normalized, env_dict)
            except Exception:
                # 3. Fallback to eval_ast for complex dynamic features
                pass
        return eval_ast(node, env)
