import sys
import os
from .types import *
from .compression import comp_map, comp_options_map, comp_str_map


class SquashfsMaker(object):
    """docstring for SquashfsMaker"""
    def __init__(self):
        super(SquashfsMaker, self).__init__()
        self.to_pack = []           # items to pack (the user insert here what do he want to be packed into squashfs filesystem)
        self.path = './'
        self.comp = None
        self.block_size = 0x1000    # set the max block size as the default
        self._inode_num = 1

        # the following lists needs to be packed into metadata blocks just
        # when they reach the METADATA_BLOCK_SIZE (0x2000 bytes). the first 
        # item is the size of the (unpacked) metadata in the list.
        # because the max file-system size is 256 MB, it is no so terrible for the RAM.
        self._inode_table      = [0]
        self._directory_table  = [0]
        self._fragment_table   = [0]
        self._export_table     = [0]
        self._ids_table        = [0]
        self._ids_index        = [0]
        self._xatters_table    = [0]
        self._xatter_ids_table = [0]
        self._xatter_ids_index = [0]

        # the following are the buffers themselves (just after writing all the files
        # data it can be known where to write them on the file)
        self._inode_buffer            = bytearray()
        self._directory_buffer        = bytearray()
        self._fragment_buffer         = bytearray()
        self._export_buffer           = bytearray()
        self._ids_buffer              = bytearray()
        self._ids_index_buffer        = bytearray()
        self._xatters_buffer          = bytearray()
        self._xatter_ids_buffer       = bytearray()
        self._xatter_ids_index_buffer = bytearray()

        self._dir_inodes = {}


    def _pack_dir(self, path):
        files = os.listdir(path)
        header = directory_header()
        header.count = len(files)
        header.start_block = len(self._inode_buffer)
        header.inode_number = self._inode_num = self._inode_num + 1
        self._add_metadata_item(header, self._directory_table, self._directory_buffer)

        dir_start = len(self._directory_buffer)
        dir_offset = self._directory_table[0]

        offset = 0
        size = len(header)
        for file in files:
            if os.path.isdir(path+file):
                self._dir_inodes[path+file].parent_inode_number = header.inode_number
                self._add_metadata_item(self._dir_inodes[path+file], self._inode_table, self._inode_buffer)
            else:
                self._make_indoe(path+file)
            entry = directory_entry()
            entry.offset = offset
            entry.inode_number = self._inode_table[-1].header.inode_number
            entry.type = self._inode_table[-1].header.inodes_type
            entry.size = len(file)
            entry.__init__(entry.packed+file)
            self._add_metadata_item(entry, self._directory_table, self._directory_buffer)

            offset += len(self._inode_table[-1].packed)
            size += len(entry._buf)

        self._make_dir_inode(path, dir_start, dir_offset, size)

        return None

    def _add_metadata_item(self, item, table, buffer):
        if (table[0] >= METADATA_BLOCK_SIZE) or ((table[0] + len(item.packed)) > METADATA_BLOCK_SIZE):
            self._pack_metadata_block(table)
        table.append(item)
        table[0] += len(item._buf)

    def _make_inode(self, path):
        pass

    def make_dir_inode(self, path, start_block, offset, file_size, index_count):
        pass

    def _pack_metadata_block(self, metadata):
        pass

    def _pack_data_block(self, data):
        pass


