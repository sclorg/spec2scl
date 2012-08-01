from spec2scl.decorators import matches
from spec2scl.transformers.transformer import Transformer

class RTransformer(Transformer):
    def __init__(self, spec, options = None):
        super(RTransformer, self).__init__(spec, options)

    @matches(r'R\s+CMD', one_line = False)
    def handle_R_specific_commands(self, pattern, text):
        return self.sclize_all_commands(pattern, text)
