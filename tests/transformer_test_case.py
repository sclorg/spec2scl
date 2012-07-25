class TransformerTestCase(object):
    def get_pattern_for_spec(self, patterns, spec):
        for pattern in patterns:
            if pattern.search(spec):
                return pattern

