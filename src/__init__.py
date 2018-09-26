version = "0.1"

import os
import sys
dirname = os.path.dirname(__file__)
sys.path.append(os.path.abspath(os.path.join(dirname, "cstruct2py")))

import types
from squashfsimage import SquashfsImage
