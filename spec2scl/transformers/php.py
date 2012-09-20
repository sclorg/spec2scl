from spec2scl.decorators import matches
from spec2scl.transformers.transformer import Transformer

class PHPTransformer(Transformer):
    def __init__(self, spec, options = None):
        super(PHPTransformer, self).__init__(spec, options)

    @matches(r'%{__(zts)?php}\s+', one_line = False)
    @matches(r'%{__pear}', one_line = False)
    @matches(r'%{__pecl}', one_line = False)
    def handle_php_specific_commands(self, pattern, text):
        return self.sclize_all_commands(pattern, text)
