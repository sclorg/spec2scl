import pytest

from spec2scl.transformers.R import RTransformer

from tests.transformer_test_case import TransformerTestCase, scl_enable, scl_disable


class TestRTransformer(TransformerTestCase):
    def setup_method(self, method):
        self.t = RTransformer({})

    @pytest.mark.parametrize(('spec'), [
        ('"%{__bindir}/R foo" stays'),
    ])
    def test_R_specific_commands_not_matching(self, spec):
        spec = self.make_prep(spec)
        handler = self.t.handle_R_specific_commands
        assert self.get_pattern_for_spec(handler, spec) is None

    @pytest.mark.parametrize(('spec', 'expected'), [
        ('R CMD foo bar', scl_enable + 'R CMD foo bar\n' + scl_disable),
        ('%{__bindir}/R CMD foo bar\n', scl_enable + '%{__bindir}/R CMD foo bar\n' + scl_disable),
    ])
    def test_R_specific_commands_matching(self, spec, expected):
        spec = self.make_prep(spec)
        pattern = self.get_pattern_for_spec(self.t.handle_R_specific_commands, spec)
        assert pattern
        assert self.t.handle_R_specific_commands(spec, pattern, spec) == self.make_prep(expected)
