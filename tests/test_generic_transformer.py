import pytest

from spec2scl.transformers.generic import GenericTransformer

from transformer_test_case import TransformerTestCase

class TestGenericTransformer(TransformerTestCase):
    def setup_method(self, method):
        self.t = GenericTransformer('', {})

    @pytest.mark.parametrize(('spec', 'expected'), [
        ('', '%{?scl:%scl_package TODO}\n%{!?scl:%global pkg_name %{name}}'),
        ('Name:spam', '%{?scl:%scl_package spam}\n%{!?scl:%global pkg_name %{name}}'),
        ('Name: \tspam', '%{?scl:%scl_package spam}\n%{!?scl:%global pkg_name %{name}}'),
        ('Name: python-%{spam}', '%{?scl:%scl_package python-%{spam}}\n%{!?scl:%global pkg_name %{name}}'),
    ])
    def test_insert_scl_init(self, spec, expected):
        self.t.original_spec = spec # need to assign it here, because Name is taken from original spec
        assert self.t.insert_scl_init(self.t.insert_scl_init.matches[0], spec).find(expected) != -1

    @pytest.mark.parametrize(('spec', 'expected'), [
        ('Conflicts:spam', 'Conflicts:%{?scl_prefix}spam'),
        ('BuildConflicts: \t spam', 'BuildConflicts: \t %{?scl_prefix}spam'),
        ('Provides: spam < 3.0', 'Provides: %{?scl_prefix}spam < 3.0'),
        ('Conflicts: spam > 2.0-1', 'Conflicts: %{?scl_prefix}spam > 2.0-1'),
        ('Obsoletes: spam, blah, foo', 'Obsoletes: %{?scl_prefix}spam, %{?scl_prefix}blah, %{?scl_prefix}foo'),
        ('Obsoletes: spam blah foo', 'Obsoletes: %{?scl_prefix}spam %{?scl_prefix}blah %{?scl_prefix}foo'),
    ])
    def test_handle_dependency_tag(self, spec, expected):
        patterns = self.t.handle_dependency_tag.matches
        assert self.t.handle_dependency_tag(self.get_pattern_for_spec(patterns, spec), spec) == expected

    @pytest.mark.parametrize(('spec', 'expected'), [
        ('Requires: perl(:MODULE_COMPAT_%(eval "`perl -V:version`"; echo $version))',
         'Requires: %{?scl_prefix}perl(:MODULE_COMPAT_%(eval "`perl -V:version`"; echo $version))'),
        # this test case will fail, we would need something more powerful than regexps to parse nested braces
        #('Requires: spam(foo()) = 1 bar(foo()) = 2', 'a', 'Requires: %{?scl_prefix}spam(foo()) = 1 %{?scl_prefix}bar(foo()) = 2'),

    ])
    def test_handle_dependency_tag_with_spaces_in_brackets(self, spec, expected):
        patterns = self.t.handle_dependency_tag.matches
        assert self.t.handle_dependency_tag(self.get_pattern_for_spec(patterns, spec), spec) == expected

    @pytest.mark.parametrize(('spec', 'expected'), [
        ('Requires: /foo/spam', 'Requires: %{?_scl_root}/foo/spam'),
        ('Requires: spam /foo/eggs', 'Requires: %{?scl_prefix}spam %{?_scl_root}/foo/eggs'),
    ])
    def test_handle_dependency_tag_with_path(self, spec, expected):
        patterns = self.t.handle_dependency_tag.matches
        assert self.t.handle_dependency_tag(self.get_pattern_for_spec(patterns, spec), spec) == expected

    @pytest.mark.parametrize(('spec', 'scl_requires', 'expected'), [
        ('Requires: spam = %{epoch}:%{version}-%{release}', 'a', 'Requires: %{?scl_prefix}spam = %{epoch}:%{version}-%{release}'),
        ('Requires: spam > 1, spam < 3', 'a', 'Requires: %{?scl_prefix}spam > 1, %{?scl_prefix}spam < 3'),
        ('BuildRequires: python-%{spam}', 'a', 'BuildRequires: %{?scl_prefix}python-%{spam}'),
        ('BuildRequires: python-%{spam}', 'n', 'BuildRequires: python-%{spam}'),
        ('Requires: spam > 1, spam < 3', ['eggs'], 'Requires: spam > 1, spam < 3'),
        ('Requires: spam > 1, spam < 3', ['spam'], 'Requires: %{?scl_prefix}spam > 1, %{?scl_prefix}spam < 3'),
        ('BuildRequires: python(spam)', ['python(spam)', 'spam'], 'BuildRequires: %{?scl_prefix}python(spam)'),
    ])
    def test_handle_dependency_tag_modified_scl_requires(self, spec, scl_requires, expected):
        patterns = self.t.handle_dependency_tag_modified_by_list.matches
        if scl_requires:
            self.t.options = {'scl_requires': scl_requires}
        assert self.t.handle_dependency_tag_modified_by_list(self.get_pattern_for_spec(patterns, spec), spec) == expected

    @pytest.mark.parametrize(('spec', 'expected'), [
        ('%package \t -n spam', '%package \t -n %{?scl_prefix}spam'),
        ('%description -n spam', '%description -n %{?scl_prefix}spam'),
        ('%files -n   spam', '%files -n   %{?scl_prefix}spam'),
    ])
    def test_handle_subpackages_should_sclize(self, spec, expected):
        patterns = self.t.handle_subpackages.matches
        assert self.t.handle_subpackages(self.get_pattern_for_spec(patterns, spec), spec) == expected

    @pytest.mark.parametrize(('spec', 'expected'), [
        ('%package spam', '%package spam'),
        ('%description -x spam', '%description -x spam'),
        ('%files -nnn spam', '%files -nnn spam'),
    ])
    def test_handle_subpackages_should_not_sclize(self, spec, expected):
        patterns = self.t.handle_subpackages.matches
        assert self.get_pattern_for_spec(patterns, spec) == None

    @pytest.mark.parametrize(('spec', 'expected'), [
        ('%setup', '%setup -n %{pkg_name}-%{version}'),
        ('%setup -q -c -T', '%setup -n %{pkg_name}-%{version} -q -c -T'),
    ])
    def test_handle_setup_macro_should_sclize(self, spec, expected):
        assert self.t.handle_setup_macro(self.t.handle_setup_macro.matches[0], spec) == expected

    @pytest.mark.parametrize(('spec', 'expected'), [
        ('%setup -n spam', '%setup -n spam'),
        ('%setup -q -n spam -c', '%setup -q -n spam -c'),
    ])
    def test_handle_setup_macro_should_not_sclize(self, spec, expected):
        assert self.t.handle_setup_macro(self.t.handle_setup_macro.matches[0], spec) == expected

    @pytest.mark.parametrize(('spec', 'expected'), [
        ('Name: spam', 'Name: %{?scl_prefix}spam'),
        ('Name:spam', 'Name:%{?scl_prefix}spam'),
        ('Name:  %{?spam}spam', 'Name:  %{?scl_prefix}%{?spam}spam'),
    ])
    def test_handle_name_tag(self, spec, expected):
        assert self.t.handle_name_tag(self.t.handle_name_tag.matches[0], spec) == expected

    @pytest.mark.parametrize(('spec', 'expected'), [
        ('%{name}', '%{pkg_name}'),
        ('%{pkg_name}', '%{pkg_name}'),
        ('%{name_spam}', '%{name_spam}'),
    ])
    def test_handle_name_macro(self, spec, expected):
        assert self.t.handle_name_macro(self.t.handle_name_macro.matches[0], spec) == expected

    @pytest.mark.parametrize(('spec', 'meta_runtime_dep', 'expected'), [
        ('Requires:', False, 'Requires:'),
        ('Requires:', True, '%{?scl:Requires: %{scl}-runtime}\nRequires:'),
    ])
    def test_handle_meta_runtime_dep(self, spec, meta_runtime_dep, expected):
        self.t.options['meta_runtime_dep'] = meta_runtime_dep
        assert self.t.handle_meta_runtime_dep(None, spec) == expected

    @pytest.mark.parametrize(('spec', 'expected'), [
        ('configure\n', '%{?scl:scl enable %{scl} "}\nconfigure\n%{?scl:"}\n'),
        ('%configure ', '%{?scl:scl enable %{scl} "}\n%configure %{?scl:"}\n'),
        ('%configure --foo \\n --bar', '%{?scl:scl enable %{scl} "}\n%configure --foo \\n --bar%{?scl:"}\n'),
        ('make ', '%{?scl:scl enable %{scl} "}\nmake %{?scl:"}\n'),
        ('make foo\n', '%{?scl:scl enable %{scl} "}\nmake foo\n%{?scl:"}\n'),
    ])
    def test_handle_name_macro(self, spec, expected):
        patterns = self.t.handle_configure_make.matches
        assert self.t.handle_configure_make(self.get_pattern_for_spec(patterns, spec), spec) == expected
