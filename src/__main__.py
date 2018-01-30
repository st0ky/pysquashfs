from time import localtime
import os
import sys
from squashfs_operations_1 import SquashFSOps1
from squashfs_operations_2 import SquashFSOps2
from squashfs_operations_3 import SquashFSOps3
from squashfs_operations_4 import SquashFSOps4

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(here, "cstruct2py"))
import cstruct2py

squashfs_tools_src = os.path.join(here, "..", "squashfs-tools")

import IPython


types_le = cstruct2py.c2py.Parser(cstruct2py.configuration.gcc_x86_64_le)
types_le.parse_file("./includes.h", [squashfs_tools_src, os.path.join(here, "include"), os.path.join(here, "cstruct2py", "cstruct2py", "pycparser", "utils", "fake_libc_include")])
types_le.update_globals(globals())
types_be = cstruct2py.c2py.Parser(cstruct2py.configuration.gcc_x86_64_be)
types_be.parse_file("./includes.h", [squashfs_tools_src, os.path.join(here, "include"), os.path.join(here, "cstruct2py", "cstruct2py", "pycparser", "utils", "fake_libc_include")])
types_be.update_globals(types_le.__dict__)

# IPython.embed()

premission_table = [
	test(mask=S_IFMT, value=S_IFSOCK, position=0, mode='s' ),
	test(mask=S_IFMT, value=S_IFLNK, position=0, mode='l' ),
	test(mask=S_IFMT, value=S_IFBLK, position=0, mode='b' ),
	test(mask=S_IFMT, value=S_IFDIR, position=0, mode='d' ),
	test(mask=S_IFMT, value=S_IFCHR, position=0, mode='c' ),
	test(mask=S_IFMT, value=S_IFIFO, position=0, mode='p' ),
	test(mask=S_IRUSR, value=S_IRUSR, position=1, mode='r' ),
	test(mask=S_IWUSR, value=S_IWUSR, position=2, mode='w' ),
	test(mask=S_IRGRP, value=S_IRGRP, position=4, mode='r' ),
	test(mask=S_IWGRP, value=S_IWGRP, position=5, mode='w' ),
	test(mask=S_IROTH, value=S_IROTH, position=7, mode='r' ),
	test(mask=S_IWOTH, value=S_IWOTH, position=8, mode='w' ),
	test(mask=S_IXUSR | S_ISUID, value=S_IXUSR | S_ISUID, position=3, mode='s' ),
	test(mask=S_IXUSR | S_ISUID, value=S_ISUID, position=3, mode='S' ),
	test(mask=S_IXUSR | S_ISUID, value=S_IXUSR, position=3, mode='x' ),
	test(mask=S_IXGRP | S_ISGID, value=S_IXGRP | S_ISGID, position=6, mode='s' ),
	test(mask=S_IXGRP | S_ISGID, value=S_ISGID, position=6, mode='S' ),
	test(mask=S_IXGRP | S_ISGID, value=S_IXGRP, position=6, mode='x' ),
	test(mask=S_IXOTH | S_ISVTX, value=S_IXOTH | S_ISVTX, position=9, mode='t' ),
	test(mask=S_IXOTH | S_ISVTX, value=S_ISVTX, position=9, mode='T' ),
	test(mask=S_IXOTH | S_ISVTX, value=S_IXOTH, position=9, mode='x' ),
]

class SquashFS(object):
	def __init__(self, filename):
		super(SquashFS, self).__init__()
		self.source = filename
		self.data = None
		self.sBlk = super_block()
		self.s_ops = squashfs_operations()
		self.swap = None
		self.comp = None
		self.funcs = type("\x01", (object,), {})()
		self.funcs.squashfs_opendir = None
		self.funcs.read_fragment = None
		self.funcs.read_fragment_table = None
		self.funcs.read_block_list = None
		self.funcs.read_inode = None
		self.funcs.read_uids_guids = None

	def read_super(self):
		sBlk_4 = squashfs_super_block(self.data, SQUASHFS_START)
		
		self.swap = sBlk_4.s_magic != SQUASHFS_MAGIC
		if sBlk_4.s_magic == SQUASHFS_MAGIC and sBlk_4.s_major == 4 and sBlk_4.s_minor == 0:
			self.funcs.squashfs_opendir = SquashFSOps4.squashfs_opendir
			self.funcs.read_fragment = SquashFSOps4.read_fragment
			self.funcs.read_fragment_table = SquashFSOps4.read_fragment_table
			self.funcs.read_block_list = SquashFS.read_block_list_2
			self.funcs.read_inode = SquashFSOps4.read_inode
			self.funcs.read_uids_guids = SquashFSOps4.read_uids_guids
			self.sBlk.s = sBlk_4
			# self.comp = lookup_compressor_id(sBlk.s.compression)
			self.comp = sBlk.s.compression
			return True

		sBlk_3 = squashfs_super_block_3(self.data, SQUASHFS_START)
		if sBlk_3.s_magic != SQUASHFS_MAGIC:
			assert sBlk_3.s_magic == SQUASHFS_MAGIC_SWAP, "Can't find a SQUASHFS superblock on %s" % self.source
			sBlk_3 = types_be.squashfs_super_block_3(self.data, SQUASHFS_START)
			# raise NotImplemented("need to implement endiannes")

		sBlk = self.sBlk
		sBlk.s.s_magic = sBlk_3.s_magic
		sBlk.s.inodes = sBlk_3.inodes
		sBlk.s.mkfs_time = sBlk_3.mkfs_time
		sBlk.s.block_size = sBlk_3.block_size
		sBlk.s.fragments = sBlk_3.fragments
		sBlk.s.block_log = sBlk_3.block_log
		sBlk.s.flags = sBlk_3.flags
		sBlk.s.s_major = sBlk_3.s_major
		sBlk.s.s_minor = sBlk_3.s_minor
		sBlk.s.root_inode = sBlk_3.root_inode
		sBlk.s.bytes_used = sBlk_3.bytes_used
		sBlk.s.inode_table_start = sBlk_3.inode_table_start
		sBlk.s.directory_table_start = sBlk_3.directory_table_start
		sBlk.s.fragment_table_start = sBlk_3.fragment_table_start
		sBlk.s.lookup_table_start = sBlk_3.lookup_table_start
		sBlk.no_uids = sBlk_3.no_uids
		sBlk.no_guids = sBlk_3.no_guids
		sBlk.uid_start = sBlk_3.uid_start
		sBlk.guid_start = sBlk_3.guid_start
		sBlk.s.xattr_id_table_start = SQUASHFS_INVALID_BLK

# 		/* Check the MAJOR & MINOR versions */
		s_ops = self.s_ops
		if sBlk.s.s_major == 1 or sBlk.s.s_major == 2:
			sBlk.s.bytes_used = sBlk_3.bytes_used_2
			sBlk.uid_start = sBlk_3.uid_start_2
			sBlk.guid_start = sBlk_3.guid_start_2
			sBlk.s.inode_table_start = sBlk_3.inode_table_start_2
			sBlk.s.directory_table_start = sBlk_3.directory_table_start_2
		
			if sBlk.s.s_major == 1:
				sBlk.s.block_size = sBlk_3.block_size_1
				sBlk.s.fragment_table_start = sBlk.uid_start
				self.funcs.squashfs_opendir = SquashFSOps1.squashfs_opendir
				self.funcs.read_fragment_table = SquashFSOps1.read_fragment_table
				self.funcs.read_block_list = SquashFSOps1.read_block_list
				self.funcs.read_inode = SquashFSOps1.read_inode
				self.funcs.read_uids_guids = SquashFSOps1.read_uids_guids

			else:
				sBlk.s.fragment_table_start = sBlk_3.fragment_table_start_2
				self.funcs.squashfs_opendir = SquashFSOps1.squashfs_opendir
				self.funcs.read_fragment = SquashFSOps2.read_fragment
				self.funcs.read_fragment_table = SquashFSOps2.read_fragment_table
				self.funcs.read_block_list = SquashFSOps2.read_block_list
				self.funcs.read_inode = SquashFSOps2.read_inode
				self.funcs.read_uids_guids = SquashFSOps1.read_uids_guids

		elif sBlk.s.s_major == 3:
			self.funcs.squashfs_opendir = SquashFSOps3.squashfs_opendir
			self.funcs.read_fragment = SquashFSOps3.read_fragment
			self.funcs.read_fragment_table = SquashFSOps3.read_fragment_table
			self.funcs.read_block_list = SquashFSOps2.read_block_list
			self.funcs.read_inode = SquashFSOps3.read_inode
			self.funcs.read_uids_guids = SquashFSOps1.read_uids_guids

		else:
			raise ValueError("Filesystem on %s is (%d:%d), " % (source, sBlk.s.s_major, sBlk.s.s_minor) + "which is a later filesystem version than I support!\n")

# 	/*
# 	 * 1.x, 2.x and 3.x filesystems use gzip compression.
# 	 */
# 	comp = lookup_compressor("gzip")
		return True

# failed_mount:
# 	return FALSE



	def print_filename(pathname, inode):
		print "mode=%s, uid=%d, gid=%d" % (SquashFS.get_mode(indoe.mode), indoe.uid, indoe.gid)

		t = localtime(inode.time)

		# print "%d-%02d-%02d %02d:%02d %s" % (t->tm_year + 1900, t->tm_mon + 1,
		# 			t->tm_mday, t->tm_hour, t->tm_min, pathname)

		# if((inode->mode & S_IFMT) == S_IFLNK)
		# printf(" -> %s", inode->symlink)


	@staticmethod
	def get_mode(mode):
		s = "----------"
		for t in premission_table:
			if mode & t.mask == t.value:
				s[t.position] = chr(t.mode)
		return s
		