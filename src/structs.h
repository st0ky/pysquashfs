typedef unsigned short int u8;
typedef unsigned int u16;
typedef unsigned long u32;
typedef unsigned long long u64;
typedef short int i8;
typedef int i16;
typedef long i32;
typedef long long i64;


//Superblock Flags
#define UNCOMPRESSED_INODES = 0x0001				//Inodes are stored uncompressed. For backward compatibility reasons, UID/GIDs are also stored uncompressed.
#define UNCOMPRESSED_DATA = 0x0002				//Data are stored uncompressed
#define CHECK = 0x0004				//Unused in squashfs 4+. Should always be unset
#define UNCOMPRESSED_FRAGMENTS = 0x0008				//Fragments are stored uncompressed
#define NO_FRAGMENTS = 0x0010				//Fragments are not used. Files smaller than the block size are stored in a full block.
#define ALWAYS_FRAGMENTS = 0x0020				//If the last block of a file is smaller than the block size, it will be instead stored as a fragment
#define DUPLICATES = 0x0040				//Identical files are recognized, and stored only once
#define EXPORTABLE = 0x0080				//Filesystem has support for export via NFS (The export table is populated)
#define UNCOMPRESSED_XATTRS = 0x0100				//Xattrs are stored uncompressed
#define NO_XATTRS = 0x0200				//Xattrs are not stored
#define COMPRESSOR_OPTIONS = 0x0400				//The compression options section is present
#define UNCOMPRESSED_IDS = 0x0800				//UID/GIDs are stored uncompressed. Note that the UNCOMPRESSED_INODES flag also has this effect. If that flag is set, this flag has no effect. This flag is currently only available on master in git, no released version of squashfs yet supports it.

//inode types
#define BASIC_DIRECTORY = 1
#define BASIC_FILE = 2
#define BASIC_SYMLINK = 3
#define BASIC_BLOCK_DEVICE = 4
#define BASIC_CHAR_DEVICE = 5
#define BASIC_FIFO = 6
#define BASIC_SOCKET = 7
#define EXTENDED_DIRECTORY = 8
#define EXTENDED_FILE = 9
#define EXTENDED_SYMLINK = 10
#define EXTENDED_BLOCK_DEVICE = 11
#define EXTENDED_CHAR_DEVICE = 12
#define EXTENDED_FIFO = 13
#define XTENDED_SOCKET = 14


typedef struct superblock{
	u32 magic;
	u32 inode_count;
	i32 modification_time;
	u32 block_size;
	u32 fragment_entry_count;
	u16 compression_id;
	u16 block_log;
	u16 flags;
	u16 id_count;
	u16 version_major;
	u16 version_minor;
	u64 root_inod_ref;
	u64 id_table_start;
	u64 xattr_id_table_start;
	u64 inode_table_start;
	u64 directory_table_start;
	u64 fragment_table_start;
	u64 export_table_start;
}super_block;

typedef struct inodeheader{
	u16	inode_type;
	u16	permission;
	u16	uid_idx;
	u16 gid_idx;
	i32 modiied_time;
	u32 inode_number;
}inode_header;

typedef struct basicdirectory{
	inode_header header;
	u32 start_block;
	u32 nlink;
	u16 file_size;
	u16 offset;
	u32 parent_inode_number;

}basic_directory;

typedef struct basicfile{
	inode_header header;
	u32 blocks_start;
	u32 fragment_block_index;
	u32 fragment_offset;
	u32 file_size;
	u32 block_sizes;
}basic_file;

typedef struct basicsymlink{
	inode_header header;
	u32 nlink;
	u32 target_size;
	u8 target_path;
}basic_symlink;

typedef struct basicblockdevice{
	inode_header header;
	u32 nlink;
	u32 device;
}basic_block_device;

typedef struct basicchardevice{
	inode_header header;
	u32 nlink;
	u32 device;
}basic_char_device;

typedef struct basicfifo{
	inode_header header;
	u32 nlink;
}basic_fifo;

typedef struct basicsocket{
	inode_header header;
	u32 nlink;
}basic_socket;

typedef struct extendeddirectory{
	inode_header header;
}extended_directory;

typedef struct extendedfile{
	inode_header header;
}extended_file;

typedef struct extendedsymlink{
	inode_header header;
}extended_symlink;

typedef struct extendedblockdevice{
	inode_header header;
}extended_block_device;

typedef struct extendedchardevice{
	inode_header header;
}extended_char_device;

typedef struct xtendedsocket{
	inode_header header;
}xtended_socket;
