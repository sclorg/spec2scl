from rpm2scl.transformers.transformer import Transformer
from rpm2scl.settings import *

class Convertor(object):
    def __init__(self, spec, options = None):
        self.spec = spec
        self.options = options or {}

        self.fix_split_spec()

    def fix_split_spec(self):
        if not isinstance(self.spec, str):
            self.spec = ''.join(self.spec)

    def convert(self):
        return Transformer(self.spec, self.options).transform()
