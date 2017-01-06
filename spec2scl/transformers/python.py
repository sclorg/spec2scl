from spec2scl import transformer
from spec2scl.decorators import matches


@transformer.Transformer.register_transformer
class PythonTransformer(transformer.Transformer):
    def __init__(self, options={}):
        super(PythonTransformer, self).__init__(options)

    @matches(r'%{__python\d*}\s+', one_line=False)
    @matches(r'nosetests', one_line=False)
    @matches(r'py\.test', one_line=False)
    @matches(r'sphinx-', one_line=False)
    def handle_python_specific_commands(self, original_spec, pattern, text):
        return self.sclize_all_commands(pattern, text)
