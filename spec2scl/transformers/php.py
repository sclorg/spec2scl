from spec2scl import transformer
from spec2scl.decorators import matches


@transformer.Transformer.register_transformer
class PHPTransformer(transformer.Transformer):
    def __init__(self, options={}):
        super(PHPTransformer, self).__init__(options)

    @matches(r'%{__(zts)?php}\s+', one_line=False)
    @matches(r'%{__pear}', one_line=False)
    @matches(r'%{__pecl}', one_line=False)
    def handle_php_specific_commands(self, original_spec, pattern, text):
        return self.sclize_all_commands(pattern, text)
