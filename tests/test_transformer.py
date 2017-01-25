# TODO: use mocking to test functions in isolation
import re

import pytest

from spec2scl import settings
from spec2scl.decorators import matches
from spec2scl.transformer import Transformer
from spec2scl.specfile import Specfile

from tests.transformer_test_case import TransformerTestCase, scl_enable, scl_disable


class SpamTransformer(Transformer):
    """This is a testing class to test various Transformer methods"""
    def __init__(self, options={}):
        super(SpamTransformer, self).__init__(options)

    @matches(r'spam', sections=settings.RUNTIME_SECTIONS)
    def handle_spam(self, original_spec, pattern, text):
        return text.replace('spam', 'handled spam', 1)

    @matches(r'spam\nspam', one_line=False)
    def handle_global_spam(self, original_spec, pattern, text):
        return text.replace('spam\nspam', 'handled global\nspam', 1)

    @matches(r'foo')
    def handle_foo(self, original_spec, pattern, text):
        return text.replace('foo', 'handled foo', 1)

    @matches(r'foo\nfoo', one_line=False)
    def handle_global_foo(self, original_spec, pattern, text):
        return text.replace('foo\nfoo', 'handled global\nfoo', 1)

    @matches(r'looney', one_line=False)
    def handle_simple_global_looney(self, original_spec, pattern, text):
        return self.sclize_all_commands(pattern, text)

    @matches(r'ham\s+', one_line=False)
    def handle_spam_and_space(self, original_spec, pattern, text):
        return self.sclize_all_commands(pattern, text)

    # test helper attributes/methods
    # it may be needed to alter these when something is changed in this class
    _transformer_names = set(['handle_spam', 'handle_foo', 'handle_global_spam',
                              'handle_global_foo', 'handle_simple_global_looney',
                              'handle_spam_and_space'])
    _transformer_matches = set([r'spam', r'foo', r'spam\nspam', r'foo\nfoo',
                                r'looney', r'ham\s+'])
    _transformer_one_liners = 2
    _transformer_more_liners = 4


class TestTransformer(TransformerTestCase):
    def setup_method(self, method):
        self.t = Transformer()
        self.st = SpamTransformer()

    # ========================= tests for methods that don't apply to Transformer subclasses

    @pytest.mark.parametrize(('spec', 'expected'), [
        ('nothing', 'TODO'),
        ('Name: foo', 'foo'),
        ('Name: foo', 'foo'),
        ('Name: %{spam}foo', '%{spam}foo'),
        ('Name: foo-_%{spam}', 'foo-_%{spam}'),
    ])
    def test_get_original_name(self, spec, expected):
        assert self.t.get_original_name(spec) == expected

    @pytest.mark.parametrize(('pattern', 'spec', 'expected'), [
        (re.compile(r'eat spam'), 'eat spam\neat eat spam', ['eat spam\n', 'eat eat spam']),
        (re.compile(r'eat spam'), 'eat spam\\\neat eat spam', ['eat spam\\\neat eat spam']),
        (re.compile(r'eat spam'), 'eat spam\\\neat \\ \n eat spam', ['eat spam\\\neat \\ \n eat spam']),
        (re.compile(r'eat spam'), 'spam eat\nand spam', []),
        (re.compile(r'eat spam'), 'eat spam \\\n and ham', ['eat spam \\\n and ham']),
        (re.compile(r'eat spam'), 'SPAM=SPAM eat spam', ['SPAM=SPAM eat spam']),
        (re.compile(r'eat spam'), 'SPAM=SPAM eat spam \\\n and ham', ['SPAM=SPAM eat spam \\\n and ham']),
        (re.compile(r'^spam\s+', re.MULTILINE), 'xspam\nspam ', ['spam ']),
    ])
    def test_find_whole_commands(self, pattern, spec, expected):
        assert self.t.find_whole_commands(pattern, spec) == expected

    # ========================= tests for methods that apply to Transformer subclasses

    def test_collect_transformer_methods(self):
        methods, matches, one_line, sections = zip(*self.st.collect_transformer_methods())
        # check methods
        assert set(map(lambda x: x.__name__, methods)) == self.st._transformer_names
        assert set(map(lambda x: x.pattern, matches)) == self.st._transformer_matches
        assert one_line.count(True) == self.st._transformer_one_liners
        assert one_line.count(False) == self.st._transformer_more_liners
        # TODO: check sections

    @pytest.mark.parametrize(('spec', 'expected'), [
        ('nothing to do', 'nothing to do'),
        ('foo', 'handled foo'),
        ('spam', 'handled spam'),
    ])
    def test_transform_one_liners(self, spec, expected):
        assert self.st.transform_one_liners(spec, '%prep', spec) == expected

    @pytest.mark.parametrize(('spec', 'expected'), [
        ('foo spam', 'handled foo handled spam'),
    ])
    def test_multiple_transform_one_liners_apply_on_one_line(self, spec, expected):
        assert self.st.transform_one_liners(spec, '%prep', spec) == expected

    @pytest.mark.parametrize(('spec', 'expected'), [
        ('nothing to do', 'nothing to do'),
        ('foo\nfoo', 'handled global\nfoo'),
        ('spam\nspam', 'handled global\nspam'),
        ('spam\nspam\nfoo\nfoo', 'handled global\nspam\nhandled global\nfoo'),
        ('spam\nxspam', 'spam\nxspam'),
    ])
    def test_transform_more_liners(self, spec, expected):
        assert self.st.transform_more_liners(spec, '%prep', spec) == expected

    @pytest.mark.parametrize(('spec', 'expected'), [
        ('looney\nlooney\n', '{0}looney\n{1}{0}looney\n{1}'.format(scl_enable, scl_disable)),
        ('ham\n\n', '{0}ham\n{1}\n'.format(scl_enable, scl_disable)),
    ])
    def test_transformers_dont_apply_scl_enable_twice(self, spec, expected):
        assert self.st.transform_more_liners(spec, '%prep', spec) == expected

    def test_one_line_pattern_endswith_arbitrary_space_doesnt_hang(self):
        # if one line pattern ends with \s+, then it might match multiple \n
        # therefore it won't get found in lines.split in find_whole_commands
        # (well, it didn't, now it works)
        self.st.transform_more_liners('ham\n\n', '%prep', 'ham\n\n')
        assert True  # if it didn't end in endless loop, we're fine

    @pytest.mark.parametrize(('spec'), [
        ('# ham\n'),
        ('blahblah # ham\n'),
        ('# %%gem_install - this is a comment'),
        ('%prep\n# ham\n\n'),
    ])
    def test_ignores_commented_commands(self, spec):
        assert 'enable' not in self.t.transform(spec, transformers=[SpamTransformer()])

    @pytest.mark.parametrize(('spec', 'expected'), [
        ('spam', 'spam'),
        ('%build\nspam', '%build\nhandled spam'),
    ])
    def test_transformer_only_applies_to_specified_sections(self, spec, expected):
        assert str(self.st._transform(spec, Specfile(spec))) == expected

    def test_transformer_skips_transformer_functions_if_requested(self):
        t = Transformer(options={'skip_functions': ['handle_foo', 'insert_scl_init']})
        assert str(t.transform('foo')) == 'foo'

    @pytest.mark.parametrize(('spec', 'expected'), [
        ('%build\nham \nlooney\n', '%build\n{0}ham \nlooney\n{1}'.format(scl_enable, scl_disable)),
        ('%prep\nlooney\nlooney\n\n', '%prep\n{0}looney\nlooney\n{1}'.format(scl_enable, scl_disable)),
        ('%build\nham \\\nham\nlooney\n', '%build\n{0}ham \\\nham\nlooney\n{1}'.format(scl_enable, scl_disable)),
    ])
    def test_transformer_wraps_whole_sections_in_scl_enable(self, spec, expected):
        transformed = self.t.transform(spec, transformers=[SpamTransformer()])
        assert str(transformed) == expected
