from spec2scl.decorators import matches
from spec2scl.transformer import Transformer

class RTransformer(Transformer):
    def __init__(self, original_spec, spec, options = None):
        super(RTransformer, self).__init__(original_spec, spec, options)

    @matches(r'R\s+CMD', one_line = False)
    def handle_R_specific_commands(self, pattern, text):
        return self.sclize_all_commands(pattern, text)
