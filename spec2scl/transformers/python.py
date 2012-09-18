from spec2scl.decorators import matches
from spec2scl.transformers.transformer import Transformer

class PythonTransformer(Transformer):
    def __init__(self, spec, options = None):
        super(PythonTransformer, self).__init__(spec, options)

    @matches(r'%{__python\d*}\s+', one_line = False)
    @matches(r'nosetests', one_line = False)
    @matches(r'py\.test', one_line = False)
    @matches(r'sphinx-', one_line = False)
    def handle_python_specific_commands(self, pattern, text):
        return self.sclize_all_commands(pattern, text)
