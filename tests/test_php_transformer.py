import pytest

from spec2scl.transformers.php import PHPTransformer

from tests.transformer_test_case import TransformerTestCase, scl_enable, scl_disable


class TestPHPTransformer(TransformerTestCase):
    def setup_method(self, method):
        self.t = PHPTransformer({})

    @pytest.mark.parametrize(('spec', 'expected'), [
        ('%{__php} blah blah\n', scl_enable + '%{__php} blah blah\n' + scl_disable),
        ('%{__ztsphp} blah blah\n', scl_enable + '%{__ztsphp} blah blah\n' + scl_disable),
        ('%{__pear} blah blah\n', scl_enable + '%{__pear} blah blah\n' + scl_disable),
        ('%{__pecl} blah blah\n', scl_enable + '%{__pecl} blah blah\n' + scl_disable),
    ])
    def test_php_specific_commands_matching(self, spec, expected):
        spec = self.make_prep(spec)
        pattern = self.get_pattern_for_spec(self.t.handle_php_specific_commands, spec)
        assert pattern
        assert self.t.handle_php_specific_commands(spec, pattern, spec) == self.make_prep(expected)
