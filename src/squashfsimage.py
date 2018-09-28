import sys
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

		#read the compression options (if COMPRESSOR_OPTIONS is set)
		if (self.superblock.flags & COMPRESSOR_OPTIONS) and (self.superblock.compression_id in comp_options_map):
			self.comp_options = comp_options_map[self.superblock.compression_id](self.fil.read(len(comp_options_map[self.superblock.compression_id])))
		

	def get_all_pathes(self):
		pass

	def _read_metadata_block(self, fil_offset, size, offset=0):
		self.fil.seek(fil_offset)
		data = ""

		while len(data) - offset < size:
			l = u16(self.fil.read(len(u16)))._val_property
			print hex(l)
			print hex(l & (0x8000 - 1))
			tmp = self.fil.read(l & (0x8000 - 1))

			if not l & 0x8000:
				tmp = self.comp.decompress(data)

			data += tmp

		return data

	def _read_inode(self, data, offset = 0):
		header = inode_header(data[offset:])
		inode = inode_map[header.inode_type](data[offset:])

		if header.inode_type in changed_size_inodes:
			pass #TO DO, write the changed size list and read 

		return inode
