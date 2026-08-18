"""
Graff Manifest Loader (project.gf)
Parses project.gf, evaluates configuration, and pre-binds standard library modules.
"""

import os
from parse import parser
from lexicals import lexer
from semantics import SymbolTable, Type_Infer
from eval import eval_ast, Environment
import std_lib

def load_manifest(filepath="project.gf"):
    if not os.path.exists(filepath) and os.path.exists("project.graff"):
        filepath = "project.graff"

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Graff Manifest Error: '{filepath}' not found in current directory.")

    with open(filepath, "r", encoding="utf-8") as f:
        code = f.read()

    ast = parser.parse(code, lexer=lexer)
    if not ast:
        raise RuntimeError(f"Graff Manifest Error: Failed to parse '{filepath}'.")

    # Evaluate project.gf AST
    env = Environment()
    for stmt in ast:
        eval_ast(stmt, env)

    if not env.contains("config"):
        raise RuntimeError(f"Graff Manifest Error: 'pub fix config' struct not found in '{filepath}'.")

    config_obj = env.get("config")
    fields = config_obj.fields if hasattr(config_obj, 'fields') else config_obj

    manifest_dict = {
        "name": fields.get("name", "graff-app"),
        "version": fields.get("version", "0.0.1"),
        "author": fields.get("author", "Anonymous"),
        "entry": fields.get("main_file", fields.get("entry", "main.gf")),
        "jit": fields.get("jit", True),
        "bind": fields.get("modules", fields.get("bind", [])),
    }

    # Pre-bind all modules listed in project.gf's bind array
    bind_list = manifest_dict["bind"]
    if hasattr(bind_list, 'elements'):
        bind_list = bind_list.elements

    for mod_path in bind_list:
        mod_name = str(mod_path)
        if mod_name in std_lib.STD_MODULES:
            mod_dict = std_lib.load_module(mod_name)
            if isinstance(mod_dict, dict):
                for sym_name, sym_val in mod_dict.items():
                    env.set(sym_name, sym_val)

    return env, manifest_dict
