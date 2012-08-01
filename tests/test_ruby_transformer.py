import pytest

from spec2scl.transformers.ruby import RubyTransformer

from transformer_test_case import TransformerTestCase

class TestRubyTransformer(TransformerTestCase):
    def setup_method(self, method):
        self.t = RubyTransformer('', {})

    def get_pattern_for_spec(self, patterns, spec):
        for pattern in patterns:
            if pattern.search(spec):
                return pattern

    @pytest.mark.parametrize(('spec'), [
        ('"rubygem install" string should not get modified'),
        ('"rubygem-rspec" string should not get modified'),
        ('"rubygem(rspec)" string should not get modified'),
        ('#ruby -some params string should not get modified'),
        ('neither should this ruby string'),
    ])
    def test_ruby_specific_commands_not_matching(self, spec):
        patterns = self.t.handle_ruby_specific_commands.matches
        assert self.get_pattern_for_spec(patterns, spec) == None

    @pytest.mark.parametrize(('spec', 'expected'), [
        ('gem install spam', '%{?scl:scl enable %{scl} "}\ngem install spam%{?scl:"}\n'),
        ('gem install spam \\\n --more-spam\n', '%{?scl:scl enable %{scl} "}\ngem install spam \\\n --more-spam\n%{?scl:"}\n'),
        ('RUBYOPT="-Ilib:test" rspec spec\n', '%{?scl:scl enable %{scl} - << \EOF}\nRUBYOPT="-Ilib:test" rspec spec\n%{?scl:EOF}\n'),
        ('testrb spam', '%{?scl:scl enable %{scl} "}\ntestrb spam%{?scl:"}\n'),
        ('ruby -some params', '%{?scl:scl enable %{scl} "}\nruby -some params%{?scl:"}\n'),
    ])
    def test_ruby_specific_commands_matching(self, spec, expected):
        patterns = self.t.handle_ruby_specific_commands.matches
        assert self.t.handle_ruby_specific_commands(self.get_pattern_for_spec(patterns, spec), spec) == expected
