typedef uint8_t u8;
typedef uint16_t u16;
typedef uint32_t u32;
typedef uint64_t u64;
typedef int8_t i8;
typedef int16_t i16;
typedef int32_t i32;
typedef int64_t i64;

#define SQUASHFS_MAGIC         (0x73717368)

//Superblock Flags
#define UNCOMPRESSED_INODES    (0x0001)            //Inodes are stored uncompressed. For backward compatibility reasons, UID/GIDs are also stored uncompressed.
#define UNCOMPRESSED_DATA      (0x0002)            //Data are stored uncompressed
#define CHECK                  (0x0004)            //Unused in squashfs 4+. Should always be unset
#define UNCOMPRESSED_FRAGMENTS (0x0008)            //Fragments are stored uncompressed
#define NO_FRAGMENTS           (0x0010)            //Fragments are not used. Files smaller than the block size are stored in a full block.
#define ALWAYS_FRAGMENTS       (0x0020)            //If the last block of a file is smaller than the block size, it will be instead stored as a fragment
#define DUPLICATES             (0x0040)            //Identical files are recognized, and stored only once
#define EXPORTABLE             (0x0080)            //Filesystem has support for export via NFS (The export table is populated)
#define UNCOMPRESSED_XATTRS    (0x0100)            //Xattrs are stored uncompressed
#define NO_XATTRS              (0x0200)            //Xattrs are not stored
#define COMPRESSOR_OPTIONS     (0x0400)            //The compression options section is present
#define UNCOMPRESSED_IDS       (0x0800)            //UID/GIDs are stored uncompressed. Note that the UNCOMPRESSED_INODES flag also has this effect. If that flag is set, this flag has no effect. This flag is currently only available on master in git, no released version of squashfs yet supports it.

//inode types
enum {
    BASIC_DIRECTORY = 1,
    BASIC_FILE,
    BASIC_SYMLINK,
    BASIC_BLOCK_DEVICE,
    BASIC_CHAR_DEVICE,
    BASIC_FIFO,
    BASIC_SOCKET,
    EXTENDED_DIRECTORY,
    EXTENDED_FILE,
    EXTENDED_SYMLINK,
    EXTENDED_BLOCK_DEVICE,
    EXTENDED_CHAR_DEVICE,
    EXTENDED_FIFO,
    EXTENDED_SOCKET
};

//compression ids
enum compression_enum {
	GZIP = 1,
	LZMA,
    LZO,
    XZ,
	LZ4,
	ZSTD
};

typedef struct inoderef {
    u16 offset;
    u32 block_offset;
    u16 unused;
} inode_ref;

//structs
	//super block
typedef struct superblock {
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
    inode_ref root_inod_ref;
    u64 bytes_used;
    u64 id_table_start;
    u64 xattr_id_table_start;
    u64 inode_table_start;
    u64 directory_table_start;
    u64 fragment_table_start;
    u64 export_table_start;
} super_block;

	//compression options
typedef struct GZIPcompression{
	i32 compression_level;
	i16 window_size;
	i16 strategies;
}GZIP_comression;

typedef struct XZcompression{
	i32 dictionary_size;
	i32 executable_filters;
}XZ_compression;

typedef struct LZ4compression{
	i32 version;
	i32 flags;
}LZ4_compression;

typedef struct ZSTDcompression{
	i32 compression_level;
}ZSTD_compression;

	//inodes
		//basic blocks
typedef struct inodeheader {
    u16 inode_type;
    u16 permission;
    u16 uid_idx;
    u16 gid_idx;
    i32 modified_time;
    u32 inode_number;
} inode_header;

typedef struct basicdirectory {
    inode_header header;
    u32 start_block;
    u32 nlink;
    u16 file_size;
    u16 offset;
    u32 parent_inode_number;

} basic_directory;

typedef struct basicfile {
    inode_header header;
    u32 blocks_start;
    u32 fragment_block_index;
    u32 fragment_offset;
    u32 file_size;
    u32 block_sizes[];
} basic_file;

typedef struct basicsymlink {
    inode_header header;
    u32 nlink;
    u32 target_size;
    u8 target_path[];
} basic_symlink;

typedef struct basicblockdevice {
    inode_header header;
    u32 nlink;
    u32 device;
} basic_block_device;

typedef struct basicchardevice {
    inode_header header;
    u32 nlink;
    u32 device;
} basic_char_device;

typedef struct basicfifo {
    inode_header header;
    u32 nlink;
} basic_fifo;

typedef struct basicsocket {
    inode_header header;
    u32 nlink;
}basic_socket;

		//extended blocks
typedef struct extendeddirectory {
    inode_header header;
    u32 nlink;
    u32 file_size;
    u32 start_block;
    u32 parent_inode_number;
    u16 index_count;
    u16 offset;
    u32 xattr_index;
} extended_directory;

typedef struct extendedfile {
    inode_header header;
    u64 blocks_start;
    u64 file_size;
    u64 sparse;
    u32 nlink;
    u32 fragment_block_index;
    u32 fragment_offset;
    u32 xattr_index;
    u32 block_sizes[];
} extended_file;

typedef struct extendedsymlink {
    inode_header header;
    u32 nlink;
    u32 target_size;
    u8 target_path[];
    u32 xattr_index;
} extended_symlink;

typedef struct extendedblockdevice {
    inode_header header;
    u32 nlink;
    u32 device;
    u32 xattr_index;
} extended_block_device;

typedef struct extendedchardevice {
    inode_header header;
    u32 nlink;
    u32 device;
    u32 xattr_index;
} extended_char_device;

typedef struct extendedfifo {
    inode_header header;
    u32 nlink;
    u32 xattr_index;
} extended_fifo;

typedef struct extendedsocket {
    inode_header header;
    u32 nlink;
    u32 xattr_index;
} extended_socket;

	//fragments
typedef struct fragmentblockentry{
	u64 start;
	u32 size;
	u32 unused;
}fragment_block_entry;