
import os
import re
import sys
from os.path import dirname

ta_name = "TA-anthropic_claude_enterprise"
pattern = re.compile(r"[\\/]etc[\\/]apps[\\/][^\\/]+[\\/]bin[\\/]?$")
new_paths = [path for path in sys.path if not pattern.search(path) or ta_name in path]
new_paths.insert(0, os.path.join(dirname(dirname(__file__)), "lib"))
new_paths.insert(0, dirname(__file__))
sys.path = new_paths
