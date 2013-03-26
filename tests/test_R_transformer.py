import pytest

from spec2scl.transformers.R import RTransformer

from tests.transformer_test_case import TransformerTestCase

class TestRTransformer(TransformerTestCase):
    def setup_method(self, method):
        self.t = RTransformer({})

    @pytest.mark.parametrize(('spec'), [
        ('"%{__bindir}/R foo" stays'),
    ])
    def test_R_specific_commands_not_matching(self, spec):
        spec = self.make_prep(spec)
        handler = self.t.handle_R_specific_commands
        assert self.get_pattern_for_spec(handler, spec) == None

    @pytest.mark.parametrize(('spec', 'expected'), [
        ('R CMD foo bar', '%{?scl:scl enable %{scl} "}\nR CMD foo bar%{?scl:"}\n'),
        ('%{__bindir}/R CMD foo bar\n', '%{?scl:scl enable %{scl} "}\n%{__bindir}/R CMD foo bar\n%{?scl:"}\n'),
    ])
    def test_R_specific_commands_matching(self, spec, expected):
        spec = self.make_prep(spec)
        handler = self.t.handle_R_specific_commands
        assert self.t.handle_R_specific_commands(spec, self.get_pattern_for_spec(handler, spec), spec) == self.make_prep(expected)
