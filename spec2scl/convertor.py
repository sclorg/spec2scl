import jinja2

from spec2scl import transformer


class Convertor(object):

    """The Convertor object is responsible for producing SCL-style specfiles.

    The Convertor object can either convert a conventional spec file into
    a Software Collection spec, or create a spec file for a metapackage.
    """

    def __init__(self, options=None):
        """Initializes original spec and options.

        Args:
            spec: (str|list) The original spec file.
            options: (dict|None) Options provided for the CLI command.
        """
        self.options = options or {}

    def handle_scl_deps(self):
        """Parse file with SCL dependencies provided with
        --list-file option.
        """
        self.options['scl_deps'] = True

        if self.options['no_deps_convert']:
            self.options['scl_deps'] = False

        elif self.options['list_file']:
            self.options['scl_deps'] = {}
            with open(self.options['list_file']) as list_file:
                for dependency in list_file.readlines():
                    pair = dependency.split()
                    if pair:
                        self.options['scl_deps'][pair[0]] = pair[1] if len(pair) >= 2 else ''

    def list_to_str(self, arg):
        if not isinstance(arg, str):
            arg = ''.join(arg)
        return arg

    def convert(self, spec):
        """Convert a conventional spec file into a SCL-style spec."""
        spec = self.list_to_str(spec)
        return transformer.Transformer(self.options).transform(spec)

    def create_meta_specfile(self):
        """Create a spec file for Software Collection metapackage."""
        data = transformer.MetaTransformer(
            self.options['meta_specfile'], self.options['variables'])
        jinja_env = jinja2.Environment(loader=jinja2.ChoiceLoader([
            jinja2.FileSystemLoader(['/']),
            jinja2.PackageLoader('spec2scl', 'templates'), ]))
        jinja_template = jinja_env.get_template('metapackage.spec')
        return jinja_template.render(data=data)
