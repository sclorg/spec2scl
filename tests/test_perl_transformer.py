import pytest

from spec2scl.transformers.perl import PerlTransformer

from transformer_test_case import TransformerTestCase

class TestPerlTransformer(TransformerTestCase):
    def setup_method(self, method):
        self.t = PerlTransformer('', {})

    def test_perl_doesnt_match_dynamic_dependencies_in_spec(self):
        spec = 'Requires:       %{?scl_prefix}perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))'
        patterns = self.t.handle_perl_specific_commands.matches
        assert self.get_pattern_for_spec(patterns, spec) == None

    def test_perl_transformer_doesnt_hang_on_perl_macro(self):
        # the regex was written badly so that it matched the whole spec from the
        # beginning and find_whole_commands was therefore caught in infinite loop
        spec = 'foo\n%{__perl} '
        patterns = self.t.handle_perl_specific_commands.matches
        for p in patterns:
            # general transformers also appear here, so just test all to
            # make sure we test the wanted one, too
            self.t.find_whole_commands(p, spec)
