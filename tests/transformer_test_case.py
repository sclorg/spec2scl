from spec2scl import specfile


scl_enable = '%{?scl:scl enable %{scl} - << \EOF}\nset -e\n'
scl_disable = '%{?scl:EOF}\n'


class TransformerTestCase(object):
    def make_prep(self, spec):
        # just create one of settings.RUNTIME_SECTIONS, so that we can test all the matching
        return '%prep\n' + spec

    def get_pattern_for_spec(self, handler, spec_text):
        spec = specfile.Specfile(spec_text)
        for s_name, s_text in spec.sections:
            for i, pattern in enumerate(handler.matches):
                if pattern.search(s_text) and s_name in handler.sections[i]:
                    return pattern
