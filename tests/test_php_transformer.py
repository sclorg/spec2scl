import pytest

from spec2scl.transformers.php import PHPTransformer

from tests.transformer_test_case import TransformerTestCase

class TestPythonTransformer(TransformerTestCase):
    def setup_method(self, method):
        self.t = PHPTransformer({})

    @pytest.mark.parametrize(('spec', 'expected'), [
        ('%{__php} blah blah\n', '%{?scl:scl enable %{scl} "}\n%{__php} blah blah\n%{?scl:"}\n'),
        ('%{__ztsphp} blah blah\n', '%{?scl:scl enable %{scl} "}\n%{__ztsphp} blah blah\n%{?scl:"}\n'),
        ('%{__pear} blah blah\n', '%{?scl:scl enable %{scl} "}\n%{__pear} blah blah\n%{?scl:"}\n'),
        ('%{__pecl} blah blah\n', '%{?scl:scl enable %{scl} "}\n%{__pecl} blah blah\n%{?scl:"}\n'),
    ])
    def test_python_specific_commands_matching(self, spec, expected):
        spec = self.make_prep(spec)
        handler = self.t.handle_php_specific_commands
        assert self.t.handle_php_specific_commands(spec, self.get_pattern_for_spec(handler, spec), spec) == self.make_prep(expected)
