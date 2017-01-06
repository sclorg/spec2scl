from spec2scl import settings
from spec2scl import transformer
from spec2scl.decorators import matches


@transformer.Transformer.register_transformer
class RTransformer(transformer.Transformer):
    def __init__(self, options={}):
        super(RTransformer, self).__init__(options)

    @matches(r'R\s+CMD', one_line=False, sections=settings.RUNTIME_SECTIONS)
    def handle_R_specific_commands(self, original_spec, pattern, text):
        return self.sclize_all_commands(pattern, text)
