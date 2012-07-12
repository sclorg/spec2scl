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

    @matches(r'(?<!d)(Requires:\s*)([^[\s]+)') # avoid BuildRequires
    @matches(r'(BuildRequires:\s*)([^\s]+)')
    @matches(r'(?<!d)(Conflicts:\s*)([^\s]+)') # avoid BuildConflicts
    @matches(r'(BuildConflicts:\s*)([^\s]+)')
    @matches(r'(Provides:\s*)([^\s]+)')
    @matches(r'(Obsoletes:\s*)([^\s]+)')
    def handle_dependency_tag(self, pattern, text):
        temp = pattern.sub(r'\1%{?scl_prefix}\2', text)
        # handle more Requires on one line, too
        def handle_comma(matchobj):
            return '{0}%{{?scl_prefix}}{1}'.format(matchobj.group(1), matchobj.group(2))

        comma_re = re.compile(r'(,\s*)([^\s,]+)')
        return comma_re.sub(handle_comma, temp)

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
