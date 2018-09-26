import os
import cstruct2py
from cstruct2py.configuration import gcc_x86_64_le

conf = cstruct2py.configuration.Config(gcc_x86_64_le.byteorder, gcc_x86_64_le.long_size,
										gcc_x86_64_le.ptr_size, 1)

p = cstruct2py.c2py.Parser(conf)
p.parse_file(os.path.abspath(os.path.join(os.path.dirname(__file__), "structs.h")))
p.update_globals(globals())