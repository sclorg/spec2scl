import pytest

from spec2scl.transformers.python import PythonTransformer

from tests.transformer_test_case import TransformerTestCase, scl_enable, scl_disable


class TestPythonTransformer(TransformerTestCase):
    def setup_method(self, method):
        self.t = PythonTransformer({})

    @pytest.mark.parametrize(('spec', 'expected'), [
        ('%{__python} setup.py test\n', scl_enable + '%{__python} setup.py test\n' + scl_disable),
        ('py.test bar\n', scl_enable + 'py.test bar\n' + scl_disable),
        ('nosetests foo\n', scl_enable + 'nosetests foo\n' + scl_disable),
        ('sphinx-build\n', scl_enable + 'sphinx-build\n' + scl_disable),
    ])
    def test_python_specific_commands_matching(self, spec, expected):
        spec = self.make_prep(spec)
        pattern = self.get_pattern_for_spec(self.t.handle_python_specific_commands, spec)
        assert pattern
        assert self.t.handle_python_specific_commands(spec, pattern, spec) == self.make_prep(expected)
