import re

class Specfile(object):
    def __init__(self, specfile):
        if not isinstance(specfile, str):
            self.specfile = ''.join(specfile)
        else:
            self.specfile = specfile

        self.sections = self.split_sections()
    
    def split_sections(self):
        headers_re = [re.compile(x, re.M) for x in [r'^%description',
                                                    r'^%package',
                                                    r'^%prep',
                                                    r'^%build',
                                                    r'^%install',
                                                    r'^%clean',
                                                    r'^%check',
                                                    r'^%files',
                                                    r'^%changelog']]
        section_starts = []
        for header in headers_re:
            for match in header.finditer(self.specfile):
                section_starts.append(match.start())

        section_starts.sort()
        sections = [('%header', self.specfile[:section_starts[0]])]
        for i in range(len(section_starts)):
            if len(section_starts) > i + 1:
                curr_section = self.specfile[section_starts[i]:section_starts[i+1]]
            else:
                curr_section = self.specfile[section_starts[i]:]
            for header in headers_re:
                if header.match(curr_section):
                    sections.append((header.pattern[1:], curr_section))

        return sections
