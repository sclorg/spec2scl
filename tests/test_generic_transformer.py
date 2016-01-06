import pytest

from spec2scl.transformers.generic import GenericTransformer

from tests.transformer_test_case import TransformerTestCase, scl_enable, scl_disable


class TestGenericTransformer(TransformerTestCase):
    def setup_method(self, method):
        self.t = GenericTransformer({})

    @pytest.mark.parametrize(('spec', 'expected'), [
        ('', '%{?scl:%scl_package TODO}\n%{!?scl:%global pkg_name %{name}}'),
        ('Name:spam', '%{?scl:%scl_package spam}\n%{!?scl:%global pkg_name %{name}}'),
        ('Name: \tspam', '%{?scl:%scl_package spam}\n%{!?scl:%global pkg_name %{name}}'),
        ('Name: python-%{spam}', '%{?scl:%scl_package python-%{spam}}\n%{!?scl:%global pkg_name %{name}}'),
    ])
    def test_insert_scl_init(self, spec, expected):
        self.t.original_spec = spec  # need to assign it here, because Name is taken from original spec
        assert self.t.insert_scl_init(spec, self.t.insert_scl_init.matches[0], spec).find(expected) != -1

    @pytest.mark.parametrize(('spec', 'expected'), [
        ('Conflicts:spam', 'Conflicts:%{?scl_prefix}spam'),
        ('BuildConflicts: \t spam', 'BuildConflicts: \t %{?scl_prefix}spam'),
        ('Provides: spam < 3.0', 'Provides: %{?scl_prefix}spam < 3.0'),
        ('Provides: bundled(libname)', 'Provides: bundled(libname)'),
        ('Conflicts: spam > 2.0-1', 'Conflicts: %{?scl_prefix}spam > 2.0-1'),
        ('Obsoletes: spam, blah, foo', 'Obsoletes: %{?scl_prefix}spam, %{?scl_prefix}blah, %{?scl_prefix}foo'),
        ('Obsoletes: spam blah foo', 'Obsoletes: %{?scl_prefix}spam %{?scl_prefix}blah %{?scl_prefix}foo'),
    ])
    def test_handle_dependency_tag(self, spec, expected):
        pattern = self.get_pattern_for_spec(self.t.handle_dependency_tag, spec)
        if pattern:
            assert self.t.handle_dependency_tag(spec, pattern, spec) == expected
        else:
            assert spec == expected

    @pytest.mark.parametrize(('spec', 'expected'), [
        ('Requires: perl(:MODULE_COMPAT_%(eval "`perl -V:version`"; echo $version))',
         'Requires: %{?scl_prefix}perl(:MODULE_COMPAT_%(eval "`perl -V:version`"; echo $version))'),
        # this test case will fail, we would need something more powerful than regexps to parse nested braces
        # ('Requires: spam(foo()) = 1 bar(foo()) = 2', 'a', 'Requires: %{?scl_prefix}spam(foo()) = 1 %{?scl_prefix}bar(foo()) = 2'),

    ])
    def test_handle_dependency_tag_with_spaces_in_brackets(self, spec, expected):
        handler = self.t.handle_dependency_tag
        assert self.t.handle_dependency_tag(spec, self.get_pattern_for_spec(handler, spec), spec) == expected

    @pytest.mark.parametrize(('spec', 'expected'), [
        ('Requires: /foo/spam', 'Requires: %{?_scl_root}/foo/spam'),
        ('Requires: spam /foo/eggs', 'Requires: %{?scl_prefix}spam %{?_scl_root}/foo/eggs'),
    ])
    def test_handle_dependency_tag_with_path(self, spec, expected):
        handler = self.t.handle_dependency_tag
        assert self.t.handle_dependency_tag(spec, self.get_pattern_for_spec(handler, spec), spec) == expected

    @pytest.mark.parametrize(('spec', 'scl_deps', 'expected'), [
        ('Requires: spam = %{epoch}:%{version}-%{release}', True, 'Requires: %{?scl_prefix}spam = %{epoch}:%{version}-%{release}'),
        ('Requires: spam > 1, spam < 3', True, 'Requires: %{?scl_prefix}spam > 1, %{?scl_prefix}spam < 3'),
        ('BuildRequires: python-%{spam}', True, 'BuildRequires: %{?scl_prefix}python-%{spam}'),
        ('BuildRequires: python-%{spam}', False, 'BuildRequires: python-%{spam}'),
        ('Requires: spam > 1, spam < 3', {'eggs': ''}, 'Requires: spam > 1, spam < 3'),
        ('Requires: spam > 1, spam < 3', {'spam': ''}, 'Requires: %{?scl_prefix}spam > 1, %{?scl_prefix}spam < 3'),
        ('BuildRequires: python(spam)', {'python(spam)': '', 'spam': ''}, 'BuildRequires: %{?scl_prefix}python(spam)'),
        ('BuildRequires: python(spam)', {'python(spam)': '%{?scl_prefix_python27}'}, 'BuildRequires: %{?scl_prefix_python27}python(spam)'),
        ('BuildRequires: spam', {'egg': '%{?scl_prefix_python27}'}, 'BuildRequires: spam'),
    ])
    def test_handle_dependency_tag_modified_scl_deps(self, spec, scl_deps, expected):
        handler = self.t.handle_dependency_tag_modified_by_list
        self.t.options = {'scl_deps': scl_deps}
        assert self.t.handle_dependency_tag_modified_by_list(spec, self.get_pattern_for_spec(handler, spec), spec) == expected

    @pytest.mark.parametrize(('spec', 'expected'), [
        ('%package \t -n spam', '%package \t -n %{?scl_prefix}spam'),
        ('%description -n spam', '%description -n %{?scl_prefix}spam'),
        ('%files -n   spam', '%files -n   %{?scl_prefix}spam'),
    ])
    def test_handle_subpackages_should_sclize(self, spec, expected):
        handler = self.t.handle_subpackages
        assert self.t.handle_subpackages(spec, self.get_pattern_for_spec(handler, spec), spec) == expected

    @pytest.mark.parametrize(('spec', 'expected'), [
        ('%package spam', '%package spam'),
        ('%description -x spam', '%description -x spam'),
        ('%files -nnn spam', '%files -nnn spam'),
    ])
    def test_handle_subpackages_should_not_sclize(self, spec, expected):
        handler = self.t.handle_subpackages
        assert self.get_pattern_for_spec(handler, spec) == None

    @pytest.mark.parametrize(('spec', 'expected'), [
        ('%setup', '%setup -n %{pkg_name}-%{version}'),
        ('%setup -q -c -T', '%setup -n %{pkg_name}-%{version} -q -c -T'),
    ])
    def test_handle_setup_macro_should_sclize(self, spec, expected):
        assert self.t.handle_setup_macro(spec, self.t.handle_setup_macro.matches[0], spec) == expected

    @pytest.mark.parametrize(('spec', 'expected'), [
        ('%setup -n spam', '%setup -n spam'),
        ('%setup -q -n spam -c', '%setup -q -n spam -c'),
    ])
    def test_handle_setup_macro_should_not_sclize(self, spec, expected):
        assert self.t.handle_setup_macro(spec, self.t.handle_setup_macro.matches[0], spec) == expected

    @pytest.mark.parametrize(('spec', 'expected'), [
        ('Name: spam', 'Name: %{?scl_prefix}spam'),
        ('Name:spam', 'Name:%{?scl_prefix}spam'),
        ('Name:  %{?spam}spam', 'Name:  %{?scl_prefix}%{?spam}spam'),
    ])
    def test_handle_name_tag(self, spec, expected):
        assert self.t.handle_name_tag(spec, self.t.handle_name_tag.matches[0], spec) == expected

    @pytest.mark.parametrize(('spec', 'expected'), [
        ('%{name}', '%{pkg_name}'),
        ('%{pkg_name}', '%{pkg_name}'),
        ('%{name_spam}', '%{name_spam}'),
    ])
    def test_handle_name_macro(self, spec, expected):
        assert self.t.handle_name_macro(spec, self.t.handle_name_macro.matches[0], spec) == expected

    @pytest.mark.parametrize(('spec', 'no_meta_runtime_dep', 'no_meta_buildtime_dep', 'expected'), [
        ('Requires:', True, True, 'Requires:'),
        ('Requires:', False, True, '%{?scl:Requires: %{scl}-runtime}\nRequires:'),
        ('Requires:', True, False, '%{?scl:BuildRequires: %{scl}-runtime}\nRequires:'),
        ('Requires:', False, False, '%{?scl:Requires: %{scl}-runtime}\n%{?scl:BuildRequires: %{scl}-runtime}\nRequires:'),
    ])
    def test_handle_meta_deps(self, spec, no_meta_runtime_dep, no_meta_buildtime_dep, expected):
        self.t.options['no_meta_runtime_dep'] = no_meta_runtime_dep
        self.t.options['no_meta_buildtime_dep'] = no_meta_buildtime_dep
        assert self.t.handle_meta_deps(spec, None, spec) == expected

    @pytest.mark.parametrize(('spec', 'expected'), [
        ('configure\n', scl_enable + 'configure\n' + scl_disable),
        ('%configure ', scl_enable + '%configure \n' + scl_disable),
        ('%configure --foo \\n --bar', scl_enable + '%configure --foo \\n --bar\n' + scl_disable),
        ('make ', scl_enable + 'make \n' + scl_disable),
        ('make foo\n', scl_enable + 'make foo\n' + scl_disable),
        ('  make foo\n', scl_enable + '  make foo\n' + scl_disable),
    ])
    def test_handle_configure_make(self, spec, expected):
        spec = self.make_prep(spec)
        pattern = self.get_pattern_for_spec(self.t.handle_configure_make, spec)
        assert pattern
        assert self.t.handle_configure_make(spec, pattern, spec) == self.make_prep(expected)
