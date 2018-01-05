import cstruct2py
import cstruct2py.c2py as types
import os

squashfs_tools_src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "squashfs-tools")

import IPython
# IPython.embed()
types.parse_file("./includes.h", [squashfs_tools_src, r"C:\binyam\squashfs\src\cstruct2py\pycparser\utils\fake_libc_include"], save_tmp=True, debuglevel=0)
class SquashFS(object):
	def __init__(self, arg):
		super(SquashFS, self).__init__()
		self.arg = arg
		