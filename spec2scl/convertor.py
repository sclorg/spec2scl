from spec2scl.transformer import Transformer
from spec2scl.transformers import *
from spec2scl.settings import *
from spec2scl.specfile import Specfile

class Convertor(object):
    def __init__(self, spec, options = None):
        spec = self.list_to_str(spec)
        self.original_spec = spec
        self.options = options or {}

    def list_to_str(self, arg):
        if not isinstance(arg, str):
            arg = ''.join(arg)
        return arg

    def convert(self):
        return Transformer(self.options).transform(self.original_spec)
