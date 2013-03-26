import pytest

from spec2scl.transformers.perl import PerlTransformer

from tests.transformer_test_case import TransformerTestCase

class TestPerlTransformer(TransformerTestCase):
    def setup_method(self, method):
        self.t = PerlTransformer({})

    def test_perl_transformer_doesnt_hang_on_perl_macro(self):
        # the regex was written badly so that it matched the whole spec from the
        # beginning and find_whole_commands was therefore caught in infinite loop
        spec = self.make_prep('foo\n%{__perl} ')
        patterns = self.t.handle_perl_specific_commands.matches
        for p in patterns:
            # general transformers also appear here, so just test all to
            # make sure we test the wanted one, too
            self.t.find_whole_commands(p, spec)
