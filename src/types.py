import os
import cstruct2py

p = cstruct2py.c2py.Parser()
p.parse_file(os.path.abspath(os.path.join(os.path.dirname(__file__), "structs.h")))
p.update_globals(globals())