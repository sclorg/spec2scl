import re

from spec2scl import settings
from spec2scl import transformer
from spec2scl.decorators import matches


@transformer.Transformer.register_transformer
class GenericTransformer(transformer.Transformer):

    """A collection of matching methods.

    Applies to all spec files regardless of package specifics.
    """

    def __init__(self, options={}):
        super(GenericTransformer, self).__init__(options)

    @matches(r'^', one_line=False, sections=['%header'])
    def insert_scl_init(self, original_spec, pattern, text):
        scl_init = '%{{?scl:%scl_package {0}}}\n%{{!?scl:%global pkg_name %{{name}}}}\n%if 0%{?fedora} || 0%{?rhel} >= 7\n%global brp_python_hardlink /usr/lib/rpm/brp-python-hardlink\n%else\n%global brp_python_hardlink /usr/lib/rpm/redhat/brp-python-hardlink\n%endif\n%if  0%{?rhel} == 6\n%global __os_install_post /usr/lib/rpm/brp-compress %{!?__debug_package:/usr/lib/rpm/brp-strip %{__strip}} /usr/lib/rpm/brp-strip-static-archive %{__strip} /usr/lib/rpm/brp-strip-comment-note %{__strip} %{__objdump}\n%else\n%global __os_install_post /usr/lib/rpm/brp-compress %{!?__debug_package:/usr/lib/rpm/brp-strip %{__strip}} /usr/lib/rpm/brp-strip-static-archive %{__strip} /usr/lib/rpm/brp-strip-comment-note %{__strip} %{__objdump} %{brp_python_hardlink}\n%endif'.format(self.get_original_name(original_spec))
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

            if scl_deps is True or (scl_deps_effect and scl_deps and groupdict['dep'] in scl_deps):
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

    @matches(r'(?<!d)(Requires(\([a-z]+\))?:\s*)(?!\w*/\w*)([^[\s]+)', sections=settings.METAINFO_SECTIONS)  # avoid BuildRequires
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
        # instances of name macro in these tags should be left alone because they are
        # intentionally referring to the name of the rpm we are currently processing
        if text.startswith(('Obsoletes:', 'Provides:', 'Requires:', 'BuildRequires:')):
            return text
        return pattern.sub(r'%{pkg_name}', text)

    @matches(r'.*', one_line=False, sections=['%header'])
    def handle_meta_deps(self, original_spec, pattern, text):
        runtime_dep = (
            '' if self.options['no_meta_runtime_dep']
            else '%{?scl:Requires: %{scl}-runtime}\n')

        buildtime_dep = (
            '' if self.options['no_meta_buildtime_dep']
            else '%{?scl:BuildRequires: %{scl}-runtime}\n')

        if runtime_dep or buildtime_dep:
            place_before_re = [re.compile(i, re.MULTILINE) for i in
                               ['(^BuildRequires)', '(^Requires)', '(^Name)']]
            for pb in place_before_re:
                match = pb.search(text)
                if match:
                    index = match.start(0)
                    return '{0}{1}{2}{3}'.format(text[:index], runtime_dep, buildtime_dep, text[index:])
        return text

    @matches(r'.*', one_line=False, sections=settings.RUNTIME_SECTIONS)
    def sclize_runtime_sections(self, original_spec, pattern, text):
        lines = text.splitlines(True)
        header, section = lines[0], ''.join(lines[1:])
        return '{0}{1}{2}{3}'.format(
            header, settings.SCL_ENABLE, section, settings.SCL_DISABLE)
