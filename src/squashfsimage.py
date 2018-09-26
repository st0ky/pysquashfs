from .types import *
from .compression import comp_map

class SquashfsImage(object):
	"""docstring for SquashfsImage"""
	def __init__(self, path):
		super(SquashfsImage, self).__init__()
		self.path = path

		self.fil = open(self.path)

		self.superblock = superblock(self.fil.read(len(superblock)))

		print repr(self.superblock)

		if self.superblock.version_major != 4 or self.superblock.version_minor != 0:
			raise ValueError("The module dont support this version: %d-%d" %
				(self.superblock.version_major, self.superblock.version_minor))

		assert self.superblock.magic == SQUASHFS_MAGIC
		assert self.superblock.compression_id in compression_enum

		self.comp = comp_map[self.superblock.compression_id]()

	def get_all_pathes(self):
		pass

	def _read_metadata_block(self, fil_offset, size, offset=0):
		pass
