"""A base Transformer.

Used by Convertor to perform actual transformation of a specfile.
Operates with transformer plugins defined in `transformers` package.
"""

import re

from spec2scl import specfile


class Transformer(object):

    """A base Transformer class.

    Converts tags and macro definitions in a conventional
    spec file into a Software Collection spec file.
    """

    subtransformers = []

    def __init__(self, options={}):
        self.options = options
        self.options.setdefault('skip_functions', [])
        self.options.setdefault('no_meta_runtime_dep', False)
        self.options.setdefault('no_meta_buildtime_dep', False)
        self.options.setdefault('scl_deps', True)
        self.transformer_methods = self.collect_transformer_methods()

    @classmethod
    def register_transformer(cls, t):
        """Add a transformer to subtransformers list.

        Used as a class decorator for transformer plugins.
        """
        cls.subtransformers.append(t)
        return t

    def collect_transformer_methods(self):
        """Return a list of subtransformer methods decorated with matches.

        Returns:
            list of (<method>, <pattern>, <one line>, <sections>)
        """
        transformers = []

        for method in vars(type(self)).values():
            if hasattr(method, 'matches') and method.__name__ not in self.options['skip_functions']:
                for method_number in range(len(method.matches)):
                    transformers.append(
                        (getattr(self, method.__name__), method.matches[method_number],
                         method.one_line[method_number], method.sections[method_number]))
        return transformers

    def transform_one_liners(self, original_spec, section_name, section_text):
        """Apply transformation function to each line in the spec section."""
        one_liners = list(filter(lambda x: x[2], self.transformer_methods))
        split_section = section_text.splitlines()
        for index, line in enumerate(split_section):
            for func, pattern, _, sections in one_liners:
                if section_name in sections and pattern.search(line):
                    # let all the patterns modify the line
                    line = func(original_spec, pattern, line)
                split_section[index] = line

        return '\n'.join(split_section)

    def transform_more_liners(self, original_spec, section_name, section_text):
        """Apply transformation function to whole spec section."""
        more_liners = filter(lambda x: not x[2], self.transformer_methods)
        for func, pattern, _, sections in more_liners:
            if section_name in sections and pattern.search(section_text):
                section_text = func(original_spec, pattern, section_text)

        return section_text

    def transform(self, original_spec, transformers=[]):
        """Initialize subtransformer plugins and perform
        conversion by each of them.

        Returns:
            converted spec file as a Specfile object
        """
        spec = specfile.Specfile(original_spec)
        import spec2scl.transformers  # noqa
        self.subtransformers = transformers or map(
            lambda c: c(options=self.options), type(self).subtransformers)
        for subtrans in self.subtransformers:
            spec = subtrans._transform(original_spec, spec)

        return spec

    def _transform(self, original_spec, spec):
        for i, section in enumerate(spec.sections):
            spec.sections[i] = (
                section[0], self._transform_section(original_spec, section[0], section[1]))

        return spec

    def _transform_section(self, original_spec, section_name, section_text):
        """Transform one section of a specfile.

        Apply transformation methods applicable to the whole
        section and each of it's lines.
        """
        section_text = self.transform_one_liners(
            original_spec, section_name, section_text)
        section_text = self.transform_more_liners(
            original_spec, section_name, section_text)

        return section_text

    # these methods are helpers for the actual transformations
    def get_original_name(self, original_spec):
        """Return the name of the package as defined in the specfile."""
        name_match = re.compile(r'Name:\s*([^\s]+)').search(original_spec)
        if name_match:
            return name_match.group(1)
        else:
            return 'TODO'
