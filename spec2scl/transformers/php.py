from spec2scl.decorators import matches
from spec2scl.transformer import Transformer

class PHPTransformer(Transformer):
    def __init__(self, original_spec, spec, options = None):
        super(PHPTransformer, self).__init__(original_spec, spec, options)

    @matches(r'%{__(zts)?php}\s+', one_line = False)
    @matches(r'%{__pear}', one_line = False)
    @matches(r'%{__pecl}', one_line = False)
    def handle_php_specific_commands(self, pattern, text):
        return self.sclize_all_commands(pattern, text)
