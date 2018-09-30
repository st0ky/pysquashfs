import sys
from .types import *
from .compression import comp_map

class SquashfsImage(object):
    """docstring for SquashfsImage"""
    def __init__(self, path):
        super(SquashfsImage, self).__init__()
        self.path = path
        self._block_cache = {}
        self._inode_cache = {}

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

    def get_file_content(self, path):
        pass

    def list_dir(self, path):
        pass

    def _read_metadata_block(self, fil_offset):
        if fil_offset in self._block_cache:
            return self._block_cache[fil_offset]

        self.fil.seek(fil_offset)
        l = u16(self.fil.read(len(u16)))._val_property
        data = self.fil.read(l & (0x8000 - 1))
        if not l & 0x8000:
            print "decompress..."
            data = self.comp.decompress(data)

        self._block_cache[fil_offset] = data
        return data

    def _read_metadata(self, fil_offset, size, offset=0):
        self.fil.seek(fil_offset)
        data = ""

        m = 0
        while len(data) - offset < size:
            tmp = self._read_metadata_block(fil_offset + m)
            m += len(u16) + len(tmp)
            data += tmp
        
        return data[offset:]

    def _read_inode(self, block_offset, offset):

        block_offset = block_offset*self.superblock.block_size + self.superblock.inode_table_start
        if (block_offset, offset) in self._inode_cache:
            return self._inode_cache[(block_offset, offset)]

        data = self._read_metadata(block_offset, len(inode_header) + 0x50, offset) # we read more data for the large inodes
        header = inode_header(data)
        assert header.inode_type in inode_map, "false location (file offset: {0}, offset: {1}) header:\n{2}".format(block_offset ,offset, header)
        inode = inode_map[header.inode_type](data)

        #changed size inodes (files and symlinks)
        if header.inode_type in changed_size_inodes:

            #symlinks
            if (header.inode_type == BASIC_SYMLINK) or (header.inode_type == EXTENDED_SYMLINK):
                char_size = len(u8)
                repr(inode) # for realy create the inode members (cstruct2py works lazy)
                inode_size = len(data) - len(inode.target_path) + inode.target_size*char_size
                #basic symlink
                if header.inode_type == BASIC_SYMLINK:
                    data = data[:inode_size-1]
                    inode = inode_map[header.inode_type](data)
                #extended symlink
                else:
                    index_size = len(u32)
                    inode = inode_map[header.inode_type](data[:-index_size+1])
                    inode.xattr_index = int(type(inode.xattr_index)(data[-index_size+1:]))

            #files
            if (header.inode_type == BASIC_FILE) or (header.inode_type == EXTENDED_FILE):
                data = data[:len(data)-len(data)%4] # aligne to 32bit (for block_sizes)
                inode = inode_map[header.inode_type](data)
                repr(inode) # for realy create the inode members (cstruct2py works lazy)
                block_size = len(u32)
                num_blocks = 0
                total_size = 0
                while total_size < inode.file_size:
                    total_size += inode.block_sizes[num_blocks] & DATA_BLOCK_SIZE_MASK
                    print total_size
                    print bin(inode.block_sizes[num_blocks])
                    num_blocks += 1
                inode_size = len(data) - len(inode.block_sizes) + num_blocks*block_size
                data = data[:inode_size]
                print len(data)
                inode = inode_map[header.inode_type](data)

        self._inode_cache[(block_offset, offset)] = inode
        self._inode_cache[inode.header.inode_number] = inode

        return inode