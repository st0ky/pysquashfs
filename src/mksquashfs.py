import cstruct2py
import cstruct2py.c2py as types
import os

squashfs_tools_src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "/../squashfs-tools/")

import IPython
IPython.Embed()
types.parse_file("./includes.h", )
class SquashFS(object):
	def __init__(self, arg):
		super(SquashFS, self).__init__()
		self.arg = arg
		