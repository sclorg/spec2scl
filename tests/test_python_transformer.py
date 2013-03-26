import pytest

from spec2scl.transformers.python import PythonTransformer

from tests.transformer_test_case import TransformerTestCase

class TestPythonTransformer(TransformerTestCase):
    def setup_method(self, method):
        self.t = PythonTransformer({})

    @pytest.mark.parametrize(('spec', 'expected'), [
        ('%{__python} setup.py test\n', '%{?scl:scl enable %{scl} "}\n%{__python} setup.py test\n%{?scl:"}\n'),
        ('py.test bar\n', '%{?scl:scl enable %{scl} "}\npy.test bar\n%{?scl:"}\n'),
        ('nosetests foo\n', '%{?scl:scl enable %{scl} "}\nnosetests foo\n%{?scl:"}\n'),
        ('sphinx-build\n', '%{?scl:scl enable %{scl} "}\nsphinx-build\n%{?scl:"}\n'),
    ])
    def test_python_specific_commands_matching(self, spec, expected):
        spec = self.make_prep(spec)
        handler = self.t.handle_python_specific_commands
        assert self.t.handle_python_specific_commands(spec, self.get_pattern_for_spec(handler, spec), spec) == self.make_prep(expected)
