import pytest

from spec2scl.transformers.ruby import RubyTransformer

from tests.transformer_test_case import TransformerTestCase

class TestRubyTransformer(TransformerTestCase):
    def setup_method(self, method):
        self.t = RubyTransformer({})

    @pytest.mark.parametrize(('spec'), [
        ('#ruby -some params string should not get modified'),
    ])
    def test_ruby_specific_commands_not_matching(self, spec):
        spec = self.make_prep(spec)
        handler = self.t.handle_ruby_specific_commands
        assert self.get_pattern_for_spec(handler, spec) == None

    @pytest.mark.parametrize(('spec', 'expected'), [
        ('gem install spam', '%{?scl:scl enable %{scl} "}\ngem install spam\n%{?scl:"}\n'),
        ('gem spec %{SOURCE0} -l --ruby > %{gem_name}.gemspec', '%{?scl:scl enable %{scl} "}\ngem spec %{SOURCE0} -l --ruby > %{gem_name}.gemspec\n%{?scl:"}\n'),
        ('gem install spam \\\n --more-spam\n', '%{?scl:scl enable %{scl} "}\ngem install spam \\\n --more-spam\n%{?scl:"}\n'),
        ('RUBYOPT="-Ilib:test" rspec spec\n', '%{?scl:scl enable %{scl} - << \EOF}\nRUBYOPT="-Ilib:test" rspec spec\n%{?scl:EOF}\n'),
        ('testrb spam', '%{?scl:scl enable %{scl} "}\ntestrb spam\n%{?scl:"}\n'),
        ('ruby -some params', '%{?scl:scl enable %{scl} "}\nruby -some params\n%{?scl:"}\n'),
    ])
    def test_ruby_specific_commands_matching(self, spec, expected):
        spec = self.make_prep(spec)
        handler = self.t.handle_ruby_specific_commands
        assert self.t.handle_ruby_specific_commands(spec, self.get_pattern_for_spec(handler, spec), spec) == self.make_prep(expected)
