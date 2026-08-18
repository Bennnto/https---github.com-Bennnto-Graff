"""
Gaff Programming Language Entrypoint
CLI runner & REPL for Gaff (.gf)
"""

import sys
import os

# Ensure src, addons, and cli are in Python module lookup path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, 'src'))
sys.path.insert(0, os.path.join(ROOT_DIR, 'addons'))
sys.path.insert(0, os.path.join(ROOT_DIR, 'cli'))

from cli.main import main

if __name__ == "__main__":
    main()
