import jinja2

from spec2scl import transformer


class Convertor(object):

    """The Convertor object is responsible for producing SCL-style specfiles.

    The Convertor object can either convert a conventional spec file into
    a Software Collection spec, or create a spec file for a metapackage.
    """

    def __init__(self, spec, options=None):
        """Initializes original spec and options.

        Args:
            spec: (str|list) The original spec file.
            options: (dict|None) Options provided for the CLI command.
        """
        spec = self.list_to_str(spec)
        self.original_spec = spec
        self.options = options or {}

    def list_to_str(self, arg):
        if not isinstance(arg, str):
            arg = ''.join(arg)
        return arg

    def convert(self):
        """Convert a conventional spec file into a SCL-style spec, or create
        a spec file for a metapackage, according to the --meta-specfile option.
        """
        if self.options['meta_spec']:
            return self.meta_convert()
        else:
            return transformer.Transformer(self.options).transform(self.original_spec)

    def meta_convert(self):
        """Create a spec file for Software Collection metapackage."""
        # self.original_spec contains only the scl name provided with --meta-specfile
        data = transformer.MetaTransformer(self.original_spec, self.options['variables'])
        jinja_env = jinja2.Environment(loader=jinja2.ChoiceLoader([
            jinja2.FileSystemLoader(['/']),
            jinja2.PackageLoader('spec2scl', 'templates'), ]))
        jinja_template = jinja_env.get_template('metapackage.spec')
        return jinja_template.render(data=data)
