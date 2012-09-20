import pytest

from spec2scl.transformers.R import RTransformer

from transformer_test_case import TransformerTestCase

class TestRTransformer(TransformerTestCase):
    def setup_method(self, method):
        self.t = RTransformer('', {})

    @pytest.mark.parametrize(('spec'), [
        ('"%{__bindir}/R foo" stays'),
    ])
    def test_R_specific_commands_not_matching(self, spec):
        patterns = self.t.handle_R_specific_commands.matches
        assert self.get_pattern_for_spec(patterns, spec) == None

    @pytest.mark.parametrize(('spec', 'expected'), [
        ('R CMD foo bar', '%{?scl:scl enable %{scl} "}\nR CMD foo bar%{?scl:"}\n'),
        ('%{__bindir}/R CMD foo bar\n', '%{?scl:scl enable %{scl} "}\n%{__bindir}/R CMD foo bar\n%{?scl:"}\n'),
    ])
    def test_R_specific_commands_matching(self, spec, expected):
        patterns = self.t.handle_R_specific_commands.matches
        assert self.t.handle_R_specific_commands(self.get_pattern_for_spec(patterns, spec), spec) == expected
