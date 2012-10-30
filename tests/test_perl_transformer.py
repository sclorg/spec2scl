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
