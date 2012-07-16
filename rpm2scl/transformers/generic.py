import re

from rpm2scl.decorators import matches
from rpm2scl.transformers.transformer import Transformer

class GenericTransformer(Transformer):
    def __init__(self, spec, options = None):
        super(GenericTransformer, self).__init__(spec, options)

    @matches(r'^', one_line = False)
    def insert_scl_init(self, pattern, text):
        scl_init = '%{{?scl:%scl_package {0}}}\n%{{!?scl:%global pkg_name %{{name}}}}'.format(self.get_original_name())
        return '{0}\n\n{1}'.format(scl_init, text)

    @matches(r'(?<!d)(Conflicts:\s*)([^\s]+)') # avoid BuildConflicts
    @matches(r'(BuildConflicts:\s*)([^\s]+)')
    @matches(r'(Provides:\s*)([^\s]+)')
    @matches(r'(Obsoletes:\s*)([^\s]+)')
    def handle_dependency_tag(self, pattern, text, scl_list_effect = False):
        # handle more Requires on one line
        def handle_comma(matchobj):
            version_spec_re = re.compile(r'\s*(?:>|<|=)$')
            version_start_index = version_spec_re.search(matchobj.group(2))
            require_without_version = matchobj.group(2)[0:version_start_index]

            scl_list = self.options.get('scl_list', [])
            if scl_list_effect and (scl_list == [] or require_without_version in scl_list):
                return '{0}%{{?scl_prefix}}{1}'.format(matchobj.group(1), matchobj.group(2))
            return '{0}{1}'.format(matchobj.group(1), matchobj.group(2))

        comma_re = re.compile(r'((?:,|:)\s*)([^\s,]+)')
        return comma_re.sub(handle_comma, text)

    @matches(r'(?<!d)(Requires:\s*)([^[\s]+)') # avoid BuildRequires
    @matches(r'(BuildRequires:\s*)([^\s]+)')
    def handle_dependency_tag_modified_by_list(self, pattern, text):
        return self.handle_dependency_tag(pattern, text, True)

    @matches(r'(%package\s+-n\s+)([^\s]+)')
    @matches(r'(%description\s+-n\s+)([^\s]+)')
    @matches(r'(%files\s+-n\s+)([^\s]+)')
    def handle_subpackages(self, pattern, text):
        return pattern.sub(r'\1%{?scl_prefix}\2', text)

    @matches(r'%setup')
    def handle_setup_macro(self, pattern, text):
        # only handle when -n is not present, otherwise it may be too complicated
        if text.find('-n') == -1:
            return text.replace(r'%setup', r'%setup -n %{pkg_name}-%{version}')
        else:
            return text

    @matches(r'(Name:\s*)([^\s]+)')
    def handle_name_tag(self, pattern, text):
        return pattern.sub(r'\1%{?scl_prefix}\2', text)

    @matches(r'%{name}')
    def handle_name_macro(self, pattern, text):
        return pattern.sub(r'%{pkg_name}', text)
