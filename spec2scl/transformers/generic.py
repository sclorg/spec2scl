import re

from spec2scl.decorators import matches
from spec2scl import settings
from spec2scl import transformer


@transformer.Transformer.register_transformer
class GenericTransformer(transformer.Transformer):
    def __init__(self, options={}):
        super(GenericTransformer, self).__init__(options)

    @matches(r'^', one_line=False, sections=['%header'])
    def insert_scl_init(self, original_spec, pattern, text):
        scl_init = '%{{?scl:%scl_package {0}}}\n%{{!?scl:%global pkg_name %{{name}}}}'.format(self.get_original_name(original_spec))
        return '{0}\n\n{1}'.format(scl_init, text)

    @matches(r'(?<!d)(Conflicts:\s*)([^\s]+)', sections=settings.METAINFO_SECTIONS)  # avoid BuildConflicts
    @matches(r'(BuildConflicts:\s*)([^\s]+)', sections=settings.METAINFO_SECTIONS)
    @matches(r'(Provides:\s*)(?!bundled\()([^\s]+)', sections=settings.METAINFO_SECTIONS)
    @matches(r'(Obsoletes:\s*)([^\s]+)', sections=settings.METAINFO_SECTIONS)
    def handle_dependency_tag(self, original_spec, pattern, text, scl_deps_effect=False):
        tag = text[0:text.find(':') + 1]
        deps = text[text.find(':') + 1:]
        # handle more Requires on one line

        def handle_one_dep(matchobj):
            groupdict = matchobj.groupdict('')

            scl_deps = self.options['scl_deps']

            if scl_deps == True or (scl_deps_effect and scl_deps and groupdict['dep'] in scl_deps):
                prefix = ''
                if isinstance(scl_deps, dict):
                    prefix = scl_deps[groupdict['dep']]

                if not prefix:
                    if groupdict['dep'].startswith('/'):
                        prefix = '%{?_scl_root}'
                    else:
                        prefix = '%{?scl_prefix}'

                dep = '{0}{1}'.format(prefix, groupdict['dep'])
            else:
                dep = groupdict['dep']

            return '{0}{1}{2}{3}'.format(groupdict['prespace'], dep, groupdict['ver'], groupdict['postspace'])

        dep_re = re.compile(r'(?P<prespace>\s*)(?P<dep>([^\s]+(.+\))?))(?P<ver>\s*[<>=!]+\s*[^\s]+)?(?P<postspace>\s*)')
        return tag + dep_re.sub(handle_one_dep, deps)

    @matches(r'(?<!d)(Requires:\s*)(?!\w*/\w*)([^[\s]+)', sections=settings.METAINFO_SECTIONS)  # avoid BuildRequires
    @matches(r'(BuildRequires:\s*)(?!\w*/\w*)([^\s]+)', sections=settings.METAINFO_SECTIONS)
    def handle_dependency_tag_modified_by_list(self, original_spec, pattern, text):
        return self.handle_dependency_tag(original_spec, pattern, text, True)

    @matches(r'(%package\s+-n\s+)([^\s]+)', sections=['%package'])
    @matches(r'(%description\s+-n\s+)([^\s]+)', sections=['%description'])
    @matches(r'(%files\s+-n\s+)([^\s]+)', sections=['%files'])
    def handle_subpackages(self, original_spec, pattern, text):
        return pattern.sub(r'\1%{?scl_prefix}\2', text)

    @matches(r'%setup', sections=['%prep'])
    def handle_setup_macro(self, original_spec, pattern, text):
        # only handle when -n is not present, otherwise it may be too complicated
        if text.find('-n') == -1:
            return text.replace(r'%setup', r'%setup -n %{pkg_name}-%{version}')
        else:
            return text

    @matches(r'(Name:\s*)([^\s]+)', sections=['%header'])
    def handle_name_tag(self, original_spec, pattern, text):
        return pattern.sub(r'\1%{?scl_prefix}\2', text)

    @matches(r'%{name}', sections=settings.SPECFILE_SECTIONS)
    def handle_name_macro(self, original_spec, pattern, text):
        return pattern.sub(r'%{pkg_name}', text)

    @matches(r'.*', one_line=False, sections=['%header'])
    def handle_meta_deps(self, original_spec, pattern, text):
        runtime_dep = '' if self.options['no_meta_runtime_dep'] else '%{?scl:Requires: %{scl}-runtime}\n'
        buildtime_dep = '' if self.options['no_meta_buildtime_dep'] else '%{?scl:BuildRequires: %{scl}-runtime}\n'

        if runtime_dep or buildtime_dep:
            place_before_re = [re.compile(i, re.MULTILINE) for i in ['(^BuildRequires)', '(^Requires)', '(^Name)']]
            for pb in place_before_re:
                match = pb.search(text)
                if match:
                    index = match.start(0)
                    return '{0}{1}{2}{3}'.format(text[:index], runtime_dep, buildtime_dep, text[index:])
        return text

    @matches(r'^\s*%?configure\s+', one_line=False, sections=settings.RUNTIME_SECTIONS)
    @matches(r'^\s*make\s+', one_line=False, sections=settings.RUNTIME_SECTIONS)
    def handle_configure_make(self, original_spec, pattern, text):
        return self.sclize_all_commands(pattern, text)
