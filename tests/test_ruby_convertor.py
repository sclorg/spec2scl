import pytest

from rpm2scl.transformers.ruby import RubyTransformer

class TestGenericConvertor(object):
    def setup_method(self, method):
        self.t = RubyTransformer('', {})

    def get_pattern_for_spec(self, patterns, spec):
        for pattern in patterns:
            if pattern.search(spec):
                return pattern

    @pytest.mark.parametrize(('spec', 'expected'), [
        ('"rubygem install" string should not get modified', '"rubygem install" string should not get modified'),
    ])
    def test_ruby_specific_commands_not_matching(self, spec, expected):
        patterns = self.t.handle_ruby_specific_commands.matches
        assert self.get_pattern_for_spec(patterns, spec) == None

    @pytest.mark.parametrize(('spec', 'expected'), [
        ('gem install spam', '%{?scl:scl enable %{scl} "}\ngem install spam\n%{?scl:"}\n'),
    ])
    def test_ruby_specific_commands_matching(self, spec, expected):
        patterns = self.t.handle_ruby_specific_commands.matches
        assert self.t.handle_ruby_specific_commands(self.get_pattern_for_spec(patterns, spec), spec) == expected
