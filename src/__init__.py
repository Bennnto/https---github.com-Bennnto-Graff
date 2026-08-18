import sys
import os

# Universal module path resolver for Gaff Core Engine
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SRC_DIR)
for path in (ROOT_DIR, SRC_DIR, os.path.join(ROOT_DIR, 'addons'), os.path.join(ROOT_DIR, 'cli')):
    if path not in sys.path:
        sys.path.insert(0, path)
