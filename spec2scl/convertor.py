from spec2scl.transformers.transformer import Transformer
from spec2scl.settings import *

class Convertor(object):
    def __init__(self, spec, options = None):
        spec = self.list_to_str(spec)
        # strip changelog, we don't want to transform that
        changelog_pos = spec.find('%changelog')
        self.spec = spec[:changelog_pos]
        self.changelog = spec[changelog_pos:]
        self.options = options or {}

    def list_to_str(self, arg):
        if not isinstance(arg, str):
            arg = ''.join(arg)
        return arg

    def convert(self):
        return '{0}\n\n{1}'.format(Transformer(self.spec, self.options).transform(), self.changelog)
