import pytest

from rpm2scl.transformers.R import RTransformer

class TestGenericConvertor(object):
    def setup_method(self, method):
        self.t = RTransformer('', {})

    def get_pattern_for_spec(self, patterns, spec):
        for pattern in patterns:
            if pattern.search(spec):
                return pattern

    @pytest.mark.parametrize(('spec'), [
        ('"%{bindir}/R foo" stays'),
    ])
    def test_ruby_specific_commands_not_matching(self, spec):
        patterns = self.t.handle_R_specific_commands.matches
        assert self.get_pattern_for_spec(patterns, spec) == None

    @pytest.mark.parametrize(('spec', 'expected'), [
        ('R CMD foo bar', '%{?scl:scl enable %{scl} "}\nR CMD foo bar%{?scl:"}\n'),
        ('%{bindir}/R CMD foo bar\n', '%{?scl:scl enable %{scl} "}\n%{bindir}/R CMD foo bar\n%{?scl:"}\n'),
    ])
    def test_ruby_specific_commands_matching(self, spec, expected):
        patterns = self.t.handle_R_specific_commands.matches
        assert self.t.handle_R_specific_commands(self.get_pattern_for_spec(patterns, spec), spec) == expected
