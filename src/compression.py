from .types import *

class GZipCompressor(object):
	"""docstring for GZipCompressor"""
	def __init__(self):
		super(GZipCompressor, self).__init__()
		import zlib

	def decompress(self, data):
		import zlib
		return zlib.decompress(data)


class NotImplementedCompressor(object):
	"""docstring for NotImplementedCompressor"""
	def __init__(self, *args, **kwargs):
		super(NotImplementedCompressor).__init__()
		raise NotImplementedError()


comp_map = {
	GZIP : GZipCompressor,
	LZMA : NotImplementedCompressor,
    LZO : NotImplementedCompressor,
    XZ : NotImplementedCompressor,
	LZ4 : NotImplementedCompressor,
	ZSTD : NotImplementedCompressor,
}

comp_options_map = {
	GZIP : GZIP_comression,
	XZ : XZ_compression,
	LZ4 : LZ4_compression,
	ZSTD : ZSTD_compression
}