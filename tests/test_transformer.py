import re

import pytest

from rpm2scl.transformers.transformer import Transformer

class TestGenericConvertor(object):
    def setup_method(self, method):
        self.t = Transformer('', {})

    @pytest.mark.parametrize(('pattern', 'spec', 'expected'), [
        (re.compile(r'eat spam'), 'eat spam\neat eat spam', ['eat spam\n', 'eat spam']),
        (re.compile(r'eat spam'), 'spam eat\nand spam', []),
    ])
    def test_find_whole_commands(self, pattern, spec, expected):
        assert self.t.find_whole_commands(pattern, spec) == expected
