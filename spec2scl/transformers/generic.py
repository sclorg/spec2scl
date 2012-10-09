import re

from spec2scl.decorators import matches
from spec2scl.transformers.transformer import Transformer

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
    def handle_dependency_tag(self, pattern, text, scl_requires_effect = False):
        tag = text[0:text.find(':') + 1]
        deps = text[text.find(':') + 1:]
        # handle more Requires on one line
        def handle_one_dep(matchobj):
            groupdict = matchobj.groupdict('')

            if scl_requires_effect:
                scl_requires = self.options.get('scl_requires', 'a')
            else:
                scl_requires = 'a' # convert all by default

            if scl_requires == 'a' or (not scl_requires == 'n' and groupdict['dep'] in scl_requires):
                if groupdict['dep'].startswith('/'):
                    dep = '%{{?_scl_root}}{0}'.format(groupdict['dep'])
                else:
                    dep = '%{{?scl_prefix}}{0}'.format(groupdict['dep'])
            else:
                dep = groupdict['dep']

            return '{0}{1}{2}{3}'.format(groupdict['prespace'], dep, groupdict['ver'], groupdict['postspace'])

        dep_re = re.compile(r'(?P<prespace>\s*)(?P<dep>([^\s]+(.+\))?))(?P<ver>\s*[<>=!]+\s*[^\s]+)?(?P<postspace>\s*)')
        return tag + dep_re.sub(handle_one_dep, deps)

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

    @matches(r'.*', one_line = False) # bit complicated to put it at a sane place, use whole spec
    def handle_meta_runtime_dep(self, pattern, text):
        if not self.options['meta_runtime_dep']:
            return text
        place_before_re = [re.compile(i, re.MULTILINE) for i in ['(^BuildRequires)', '(^Requires)', '(^Name)']]

        for pb in place_before_re:
            match = pb.search(text)
            if match:
                index = match.start(0)
                return '{0}%{{?scl:Requires: %{{scl}}-runtime}}\n{1}'.format(text[:index], text[index:])

    @matches(r'^%?configure\s+', one_line = False)
    @matches(r'^make\s+', one_line = False) # make is a common word, so don't take it too seriously
    def handle_configure_make(self, pattern, text):
        return self.sclize_all_commands(pattern, text)
