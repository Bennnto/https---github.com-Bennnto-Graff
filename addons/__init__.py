import sys
import os

# Universal module path resolver for Gaff Addons & Extensions
ADDONS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(ADDONS_DIR)
for path in (ROOT_DIR, ADDONS_DIR, os.path.join(ROOT_DIR, 'src'), os.path.join(ROOT_DIR, 'cli')):
    if path not in sys.path:
        sys.path.insert(0, path)
