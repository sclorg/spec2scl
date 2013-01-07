from spec2scl.decorators import matches
from spec2scl.transformers.transformer import Transformer

class PerlTransformer(Transformer):
    def __init__(self, spec, options = None):
        super(PerlTransformer, self).__init__(spec, options)

    @matches(r'^[^:\n]*%{__perl}\s+', one_line = False) # if there is a colon, it is probably a dependency, don't match that
    @matches(r'^perl\s+', one_line = False) # carefully here, "perl" will occur often in the specfile
    @matches(r'./Build', one_line = False)
    def handle_perl_specific_commands(self, pattern, text):
        return self.sclize_all_commands(pattern, text)
