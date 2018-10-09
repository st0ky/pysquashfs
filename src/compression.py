from .types import *

class GZipCompressor(object):
	"""docstring for GZipCompressor"""
	def __init__(self, comp_options = False):
		super(GZipCompressor, self).__init__()
		import zlib
		self.comp_options = comp_options

	def decompress(self, data):
		import zlib
		if self.comp_options:
			return zlib.decompress(data, wbits = self.comp_options.window_size)
		return zlib.decompress(data)

class LZMACompressor(object):
	"""docstring for GZipCompressor"""
	def __init__(self, comp_options = False):
		super(LZMACompressor, self).__init__()
		import lzma
		self.comp_options = comp_options

	def decompress(self, data):
		import lzma
		return lzma.decompress(data)

class LZ4Compressor(object):
	"""docstring for GZipCompressor"""
	def __init__(self, comp_options = False):
		super(LZ4Compressor, self).__init__()
		import lz4.frame
		self.comp_options = comp_options

	def decompress(self, data):
		import lz4.frame
		return lz4.frame.decompress(data)


class NotImplementedCompressor(object):
	"""docstring for NotImplementedCompressor"""
	def __init__(self, *args, **kwargs):
		super(NotImplementedCompressor).__init__()
		raise NotImplementedError()


comp_map = {
	GZIP : GZipCompressor,
	LZMA : LZMACompressor,
    LZO : NotImplementedCompressor,
    XZ : LZMACompressor,
	LZ4 : LZ4Compressor,
	ZSTD : NotImplementedCompressor,
}

comp_options_map = {
	GZIP : GZIP_comression,
	XZ : XZ_compression,
	LZ4 : LZ4_compression,
	ZSTD : ZSTD_compression
}

comp_str_map = {
	GZIP : 'GZIP',
	LZMA : 'LZMA',
    LZO  : 'LZO',
    XZ 	 : 'XZ',
	LZ4  : 'LZ4',
	ZSTD : 'ZSTD'
}