from spec2scl.decorators import matches
from spec2scl.transformers.transformer import Transformer

class PerlTransformer(Transformer):
    def __init__(self, spec, options = None):
        super(PerlTransformer, self).__init__(spec, options)

    @matches(r'%{__perl}\s+', one_line = False)
    @matches(r'^perl\s+', one_line = False) # carefully here, "perl" will occur often in the specfile
    @matches(r'./Build', one_line = False)
    @matches(r'^make\s+', one_line = False) # make is a common word, so don't take it too seriously
    def handle_perl_specific_commands(self, pattern, text):
        return self.sclize_all_commands(pattern, text)
