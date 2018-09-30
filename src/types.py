import os
import cstruct2py
from cstruct2py.configuration import gcc_x86_64_le

conf = cstruct2py.configuration.Config(gcc_x86_64_le.byteorder, gcc_x86_64_le.long_size,
										gcc_x86_64_le.ptr_size, 1)

p = cstruct2py.c2py.Parser(conf)
p.parse_file(os.path.abspath(os.path.join(os.path.dirname(__file__), "structs.h")))
p.update_globals(globals())

inode_map = {
	BASIC_DIRECTORY : basic_directory,	
    BASIC_FILE : basic_file,
    BASIC_SYMLINK : basic_symlink,
    BASIC_BLOCK_DEVICE : basic_block_device,
    BASIC_CHAR_DEVICE : basic_char_device,
    BASIC_FIFO : basic_fifo,
    BASIC_SOCKET : basic_socket,
    EXTENDED_DIRECTORY : extended_directory,
    EXTENDED_FILE : extended_file,
    EXTENDED_SYMLINK : extended_symlink,
    EXTENDED_BLOCK_DEVICE : extended_block_device,
    EXTENDED_CHAR_DEVICE : extended_char_device,
    EXTENDED_FIFO : extended_fifo,
    EXTENDED_SOCKET : extended_socket
}

changed_size_inodes = (BASIC_FILE, BASIC_SYMLINK, EXTENDED_FILE, EXTENDED_SYMLINK)