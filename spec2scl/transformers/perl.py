from spec2scl import settings
from spec2scl import transformer
from spec2scl.decorators import matches


@transformer.Transformer.register_transformer
class PerlTransformer(transformer.Transformer):
    def __init__(self, options={}):
        super(PerlTransformer, self).__init__(options)

    @matches(r'^[^\n]*%{__perl}\s+', one_line=False, sections=settings.RUNTIME_SECTIONS)
    @matches(r'^\s*perl\s+', one_line=False, sections=settings.RUNTIME_SECTIONS)  # carefully here, "perl" will occur often in the specfile
    @matches(r'./Build', one_line=False)
    def handle_perl_specific_commands(self, original_spec, pattern, text):
        return self.sclize_all_commands(pattern, text)
