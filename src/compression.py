from .types import *

class GZipCompressor(object):
	"""docstring for GZipCompressor"""
	def __init__(self):
		super(GZipCompressor, self).__init__()

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
