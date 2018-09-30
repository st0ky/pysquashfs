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
        prev = ""
        last = path
        if path.startswith("squashfs-root/"):
            prev = "squashfs-root/"
            last = path[len(prev):]
        elif path.startswith("/"):
            prev = "/"
            last = path[len(prev):]

        inode = self._read_inode(self.superblock.root_inod_ref.block_offset, self.superblock.root_inod_ref.offset)
        cur_dir = self._read_dir_data(inode)

        while last:
            for name, inode in cur_dir.items():
                if last.startswith(name) and (name == last or last[len(name)] == "/"):
                    prev += name + "/"
                    last = path[len(prev):]
                    cur_dir = self._read_dir_data(inode)
                    break
            else:
                raise ValueError("Cannot find %s under %s" % (repr(last), repr(prev)))

        return cur_dir

    def _read_dir_data(self, inode):
        data = self._read_metadata(self.superblock.directory_table_start + inode.start_block, inode.file_size, inode.offset)
        header = directory_header(data)
        offset = len(header)
        items = {}
        for _ in xrange(header.count+1):
            tmp = directory_entry(data, offset)
            name_size = 0
            i = self._read_inode(header.start_block, tmp.offset)
            items[data[offset + len(tmp): offset + len(tmp) + tmp.size + 1]] = i
            offset += len(tmp) + tmp.size + 1

        return items
        

    # def _read_all_dirs(self):
    #     root = self._read_inode(self.superblock.root_inod_ref.block_offset, self.superblock.root_inod_ref.offset)
    #     waiting = []
    #     waiting.append(root)
    #     result = []
    #     while waiting:
    #         i = waiting.pop()
    #         h, e = self._read_dir_data(i)
    #         result.append((i, h, e))
    #         for x in e:
    #             if x.type == BASIC_DIRECTORY:
    #                 i = self._read_inode(h.start_block, x.offset)
    #                 waiting.append(i)

    #     return result


    def _read_metadata_block(self, fil_offset):
        if fil_offset in self._block_cache:
            return self._block_cache[fil_offset]

        self.fil.seek(fil_offset)
        l = u16(self.fil.read(len(u16)))._val_property
        data = self.fil.read(l & (0x8000 - 1))
        if not l & 0x8000:
            data = self.comp.decompress(data)

        self._block_cache[fil_offset] = (data, l & (0x8000 - 1))
        return data, l & (0x8000 - 1)

    def _read_metadata(self, fil_offset, size, offset=0):
        self.fil.seek(fil_offset)
        data = ""

        m = 0
        while len(data) - offset < size:
            tmp, l = self._read_metadata_block(fil_offset + m)
            m += len(u16) + l
            data += tmp
        
        return data[offset:]

    def _read_inode(self, block_offset, offset):

        block_offset += self.superblock.inode_table_start
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
                    inode = inode_map[header.inode_type](data[:-index_size-1])
                    inode.xattr_index = int(type(inode.xattr_index)(data[-index_size+1:]))

            #files
            if (header.inode_type == BASIC_FILE) or (header.inode_type == EXTENDED_FILE):
                sums = 0
                blocks_num = 0
                data = data[:len(data) - len(data)%4]
                inode = inode_map[header.inode_type](data)
                while sums < inode.file_size:
                    sums += inode.block_sizes[blocks_num] & DATA_BLOCK_SIZE_MASK
                    blocks_num += 1
                if inode.fragment_block_index != 0xffffffff:
                    blocks_num -= 1
                print sums
                block_size = len(u32)
                inode_size = len(inode) + blocks_num*block_size
                data = data[:inode_size]
                inode = inode_map[header.inode_type](data)

        self._inode_cache[(block_offset, offset)] = inode
        self._inode_cache[inode.header.inode_number] = inode

        return inode
