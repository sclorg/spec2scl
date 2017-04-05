"""spec2scl Convertor.

Used by spec2scl and pyp2rpm CLI entry points.
"""

from spec2scl import transformer


class Convertor(object):

    """The Convertor object is responsible for producing SCL-style specfiles.

    The Convertor object converts a conventional specfile into
    a Software Collection specfile.
    """

    def __init__(self, options=None):
        """Initializes original spec and options.

        Args:
            spec: (str|list) The original spec file.
            options: (dict|None) Options provided for the CLI command.
        """
        self.options = options or {}

    def handle_scl_deps(self):
        """Parse SCL dependencies file provided with --list-file option
        and set them in `scl_deps` option.
        """
        scl_deps = True

        if self.options['no_deps_convert']:
            scl_deps = False

        elif self.options['list_file']:
            scl_deps = {}
            with open(self.options['list_file']) as list_file:
                for dependency in list_file.readlines():
                    pair = dependency.split()
                    if pair:
                        scl_deps[pair[0]] = pair[1] if len(pair) >= 2 else ''

        self.options['scl_deps'] = scl_deps

    def convert(self, spec):
        """Convert a conventional spec file into a SCL-style spec."""
        if not isinstance(spec, str):
            spec = ''.join(spec)
        return transformer.Transformer(self.options).transform(spec)
