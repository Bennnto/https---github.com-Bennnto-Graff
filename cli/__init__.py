import sys
import os

# Universal module path resolver for Gaff CLI Tools
CLI_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CLI_DIR)
for path in (ROOT_DIR, CLI_DIR, os.path.join(ROOT_DIR, 'src'), os.path.join(ROOT_DIR, 'addons')):
    if path not in sys.path:
        sys.path.insert(0, path)
