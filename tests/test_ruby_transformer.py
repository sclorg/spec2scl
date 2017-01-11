import pytest

from spec2scl.transformers.ruby import RubyTransformer

from tests.transformer_test_case import TransformerTestCase, scl_enable, scl_disable


class TestRubyTransformer(TransformerTestCase):
    def setup_method(self, method):
        self.t = RubyTransformer({})

    @pytest.mark.parametrize(('spec'), [
        ('#ruby -some params string should not get modified'),
    ])
    def test_ruby_specific_commands_not_matching(self, spec):
        spec = self.make_prep(spec)
        handler = self.t.handle_ruby_specific_commands
        assert self.get_pattern_for_spec(handler, spec) is None

    @pytest.mark.parametrize(('spec', 'expected'), [
        ('gem install spam', scl_enable + 'gem install spam\n' + scl_disable),
        ('gem spec %{SOURCE0} -l --ruby > %{gem_name}.gemspec', scl_enable + 'gem spec %{SOURCE0} -l --ruby > %{gem_name}.gemspec\n' + scl_disable),
        ('gem install spam \\\n --more-spam\n', scl_enable + 'gem install spam \\\n --more-spam\n' + scl_disable),
        ('RUBYOPT="-Ilib:test" rspec spec\n', scl_enable + 'RUBYOPT="-Ilib:test" rspec spec\n' + scl_disable),
        ('testrb spam', scl_enable + 'testrb spam\n' + scl_disable),
        ('ruby -some params', scl_enable + 'ruby -some params\n' + scl_disable),
        (' ruby -some params', scl_enable + ' ruby -some params\n' + scl_disable),
    ])
    def test_ruby_specific_commands_matching(self, spec, expected):
        spec = self.make_prep(spec)
        pattern = self.get_pattern_for_spec(self.t.handle_ruby_specific_commands, spec)
        assert pattern
        assert self.t.handle_ruby_specific_commands(spec, pattern, spec) == self.make_prep(expected)
