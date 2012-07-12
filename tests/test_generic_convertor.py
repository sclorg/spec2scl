import pytest

from rpm2scl.transformers.generic import GenericTransformer

class TestGenericConvertor(object):
    def setup_method(self, method):
        self.t = GenericTransformer('', {})

    def get_pattern_for_spec(self, patterns, spec):
        for pattern in patterns:
            if pattern.search(spec):
                return pattern

    @pytest.mark.parametrize(('spec', 'expected'), [
        ('', '%{?scl:%scl_package TODO:}\n%{!?scl:%global pkg_name %{name}}'),
        ('Name:spam', '%{?scl:%scl_package spam}\n%{!?scl:%global pkg_name %{name}}'),
        ('Name: \tspam', '%{?scl:%scl_package spam}\n%{!?scl:%global pkg_name %{name}}'),
        ('Name: python-%{spam}', '%{?scl:%scl_package python-%{spam}}\n%{!?scl:%global pkg_name %{name}}'),
    ])
    def test_insert_scl_init(self, spec, expected):
        assert self.t.insert_scl_init(self.t.insert_scl_init.matches[0], spec).find(expected)

    @pytest.mark.parametrize(('spec', 'expected'), [
        ('Requires: spam > 1, spam < 3', 'Requires: %{?scl_prefix}spam > 1, %{?scl_prefix}spam < 3'),
        ('BuildRequires: python-%{spam}', 'BuildRequires: %{?scl_prefix}python-%{spam}'),
        ('Conflicts:spam', 'Conflicts:%{?scl_prefix}spam'),
        ('BuildConflicts: \t spam', 'BuildConflicts: \t %{?scl_prefix}spam'),
        ('Provides: spam < 3.0', 'Provides: %{?scl_prefix}spam < 3.0'),
        ('Conflicts: spam > 2.0-1', 'Conflicts: %{?scl_prefix}spam > 2.0-1'),
        ('Obsoletes: spam, blah, foo', 'Obsoletes: %{?scl_prefix}spam, %{?scl_prefix}blah, %{?scl_prefix}foo'),
    ])
    def test_handle_dependency_tag(self, spec, expected):
        patterns = self.t.handle_dependency_tag.matches
        assert self.t.handle_dependency_tag(self.get_pattern_for_spec(patterns, spec), spec) == expected
