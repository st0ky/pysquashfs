import sys
from math import ceil
from .types import *
from .compression import comp_map

class SquashfsImage(object):
    """docstring for SquashfsImage"""
    def __init__(self, path):
        super(SquashfsImage, self).__init__()
        self.path = path
        self._block_cache = {}
        self._inode_cache = {}
        self._fragment_entry_cache = {}
        self._ids_cache = {}
        self._xattr_cache = {}

        self.fil = open(self.path)

        self.superblock = superblock(self.fil.read(len(superblock)))

        print repr(self.superblock)

        if self.superblock.version_major != 4 or self.superblock.version_minor != 0:
            raise ValueError("The module don't support this version: %d-%d" %
                (self.superblock.version_major, self.superblock.version_minor))

        assert self.superblock.magic == SQUASHFS_MAGIC
        assert 2**self.superblock.block_log == self.superblock.block_size
        assert self.superblock.compression_id in compression_enum

        self.comp = comp_map[self.superblock.compression_id]()

        #read the compression options (if COMPRESSOR_OPTIONS is set)
        if (self.superblock.flags & COMPRESSOR_OPTIONS) and (self.superblock.compression_id in comp_options_map):
        
            self.comp_options = comp_options_map[self.superblock.compression_id](self.fil.read(len(comp_options_map[self.superblock.compression_id])))

    def get_all_pathes(self):
        pass

    def get_file_content(self, path, size=-1, offset=0):

        filename, inode = self._get_inode_by_path(path)

        if offset > inode.file_size:
            raise ValueError("File offset %s is out of the file %s" % (offset, filename))

        r_block = inode.blocks_start
        start = offset / self.superblock.block_size
        offset = offset % self.superblock.block_size

        if size == -1:
            size = inode.file_size
        data = ""
        for i in xrange(inode.file_size / self.superblock.block_size):
            if (len(data) - offset) >= size:
                break
            elif i >= start:
                data += self._read_data_block(r_block, inode.block_sizes[i])
            r_block += inode.block_sizes[i] & DATA_BLOCK_SIZE_MASK

        if inode.fragment_block_index != 0xffffffff:
            data += self._read_fregment(inode)

        return data[offset:size+offset]
        

    def list_dir(self, path, inodes = False):
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

        if inodes:
            return cur_dir
        else:
            return sorted(cur_dir.keys())

    def _get_inode_by_path(self, path):

        begin = ""
        if path.startswith("squashfs-root/"):
            begin = "squashfs-root"
            path = path[len(begin):]
        tmp = path.split("/")
        filename = tmp[-1]
        path = begin + "/".join(tmp[:-1])

        inodes = self.list_dir(path, True)
        if not filename in inodes:
            raise ValueError("Cannot find %s under %s" % (filename, path))
        return filename, inodes[filename]


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
                blocks_num = inode.file_size / self.superblock.block_size
                if inode.fragment_block_index == 0xffffffff and inode.file_size % self.superblock.block_size:
                    blocks_num += 1
                block_size = len(u32)
                inode_size = len(inode) + blocks_num*block_size
                if inode_size > len(data):
                    data = self._read_metadata(block_offset, inode_size, offset)
                else:
                    data = data[:inode_size]
                inode = inode_map[header.inode_type](data)

        self._inode_cache[(block_offset, offset)] = inode
        self._inode_cache[inode.header.inode_number] = inode

        return inode

    def _read_data_block(self, block, size):
        compressed = not (size & DATA_BLOCK_COMPRESSED)
        size = size & DATA_BLOCK_SIZE_MASK

        self.fil.seek(block)
        data = self.fil.read(size)
        if compressed:
            data = self.comp.decompress(data)

        return data

    def _read_fregment(self, file_inode):

        assert file_inode.fragment_block_index != 0xffffffff

        frg_ent = self._read_from_index(self._fragment_entry_cache, file_inode.fragment_block_index,\
                                        fragment_block_entry, self.superblock.fragment_table_start,\
                                        self.superblock.fragment_entry_count)
        frg_size = file_inode.file_size % self.superblock.block_size
        data = self._read_data_block(frg_ent.start, frg_ent.size)
        data = data[file_inode.fragment_offset:file_inode.fragment_offset+frg_size]

        return data

    def _read_ids(self, inode):

        uid = self._read_from_index(self._ids_cache, inode.header.uid_index, id_num,\
                                     self.superblock.id_table_start, self.superblock.id_count)
        gid = self._read_from_index(self._ids_cache, inode.header.gid_index, id_num,\
                                     self.superblock.id_table_start, self.superblock.id_count)

        return {'uid': int(uid._val_property), 'gid': int(gid._val_property)}

    def _read_from_index(self, cache, indx, struct, table_start, count):

        if not 'index' in cache:
            self.fil.seek(table_start)
            num_indxs = int(ceil(count / float(METADATA_blOCK_SIZE / len(struct))))
            cache['index'] =  index(self.fil.read(num_indxs*len(u64))), num_indxs

        if indx in cache:
            data = cache[indx]

        else:
            num_block = indx / (METADATA_blOCK_SIZE / len(struct))
            offset = (indx % (METADATA_blOCK_SIZE / len(struct)))*len(struct)

            block, s = self._read_metadata_block(cache['index'][0].index[num_block])
            data = struct(block[offset:])

            cache[indx] = data

        return data

    def _read_xattr_index(self, xattr_index):

        if 'table' in self._xattr_cache:
            table = self._xattr_cache['table']
        else:
            self.fil.seek(self.superblock.xattr_id_table_start)
            table = xattr_table(self.fil.read(len(xattr_table)))
            self._xattr_cache['table'] = table

        attr_id = self._read_from_index(self._xattr_cache, xattr_index, xattr_id,\
                            self.superblock.xattr_id_table_start + len(xattr_table), table.xattr_ids)

        xattr_data = self._read_metadata(table.xattr_table_start, attr_id.size, attr_id.xattr_offset)
        xattrs_dict = {}
        offset = 0
        for i in xrange(attr_id.count):
            name, value, size = self._read_xattr(xattr_data[offset:])
            xattrs_dict[name] = value
            offset += size

        return xattrs_dict

    def _read_xattr(self, data):
        entry = xattr_entry(data)
        data = data[len(xattr_entry):]

        name = data[:entry.size]
        data = data[entry.size:]

        value_size = xattr_value(data)
        data = data[len(value_size):]

        value = data[:value_size.vsize]
        size = len(xattr_entry)+len(name)+len(xattr_value)+len(value)
        full_name = xattr_type_map[entry.type] + name

        return full_name, value, size
