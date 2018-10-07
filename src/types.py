import os
import cstruct2py
from cstruct2py.configuration import gcc_x86_64_le

conf = cstruct2py.configuration.Config(gcc_x86_64_le.byteorder, gcc_x86_64_le.long_size,
										gcc_x86_64_le.ptr_size, 1)

p = cstruct2py.c2py.Parser(conf)
p.parse_file(os.path.abspath(os.path.join(os.path.dirname(__file__), "structs.h")))
p.update_globals(globals())

inode_map = {
	BASIC_DIRECTORY       : basic_directory,	
    BASIC_FILE            : basic_file,
    BASIC_SYMLINK         : basic_symlink,
    BASIC_BLOCK_DEVICE    : basic_block_device,
    BASIC_CHAR_DEVICE     : basic_char_device,
    BASIC_FIFO            : basic_fifo,
    BASIC_SOCKET          : basic_socket,
    EXTENDED_DIRECTORY    : extended_directory,
    EXTENDED_FILE         : extended_file,
    EXTENDED_SYMLINK      : extended_symlink,
    EXTENDED_BLOCK_DEVICE : extended_block_device,
    EXTENDED_CHAR_DEVICE  : extended_char_device,
    EXTENDED_FIFO         : extended_fifo,
    EXTENDED_SOCKET       : extended_socket
}

file_type_map = {
    BASIC_DIRECTORY       : 'Directory',
    EXTENDED_DIRECTORY    : 'Directory', 
    BASIC_FILE            : 'File',
    EXTENDED_FILE         : 'File',
    BASIC_SYMLINK         : 'Symlink',
    EXTENDED_SYMLINK      : 'Symlink',
    BASIC_BLOCK_DEVICE    : 'Block device',
    EXTENDED_BLOCK_DEVICE : 'Block device',
    BASIC_CHAR_DEVICE     : 'Char device',
    EXTENDED_CHAR_DEVICE  : 'Char device',
    BASIC_FIFO            : 'Fifo',
    EXTENDED_FIFO         : 'Fifo',
    BASIC_SOCKET          : 'Socket',
    EXTENDED_SOCKET       : 'Socket'
}

is_extended_map = {
    BASIC_DIRECTORY       : False,    
    BASIC_FILE            : False,
    BASIC_SYMLINK         : False,
    BASIC_BLOCK_DEVICE    : False,
    BASIC_CHAR_DEVICE     : False,
    BASIC_FIFO            : False,
    BASIC_SOCKET          : False,
    EXTENDED_DIRECTORY    : True,
    EXTENDED_FILE         : True,
    EXTENDED_SYMLINK      : True,
    EXTENDED_BLOCK_DEVICE : True,
    EXTENDED_CHAR_DEVICE  : True,
    EXTENDED_FIFO         : True,
    EXTENDED_SOCKET       : True,
}

changed_size_inodes = (BASIC_FILE, BASIC_SYMLINK, EXTENDED_FILE, EXTENDED_SYMLINK)

xattr_type_map = {USER: 'user.', TRUSTED: 'trusted.', SECURITY: 'security.'}

permission_map = {1: 'x', 2: 'w', 0: 'r'}