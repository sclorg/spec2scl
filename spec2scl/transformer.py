import locale
import re
import subprocess
import time

from spec2scl import specfile


SCL_ENABLE = '%{?scl:scl enable %{scl} - << \EOF}\nset -e\n'
SCL_DISABLE = '%{?scl:EOF}\n'


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
        cls.subtransformers.append(t)
        return t

    def collect_transformer_methods(self):
        """Return a list of methods decorated with matches.

        Returns:
            list of tuple of (<method>, <pattern>, <one line>, <sections>)
        """
        transformers = []

        for v in vars(type(self)).values():
            if hasattr(v, 'matches'):
                for i in range(len(v.matches)):
                    transformers.append(
                        (getattr(self, v.__name__), v.matches[i], v.one_line[i], v.sections[i]))
        return transformers

    def transform_one_liners(self, original_spec, section_name, section_text):
        one_liners = list(filter(lambda x: x[2], self.transformer_methods))
        split_section = section_text.splitlines()
        skip_func = self.options['skip_functions']
        for index, line in enumerate(split_section):
            for func, pattern, _, sections in one_liners:
                if (func.__name__ not in skip_func
                    and section_name in sections
                        and pattern.search(line)):
                    # let all the patterns modify the line
                    line = func(original_spec, pattern, line)
                split_section[index] = line

        return '\n'.join(split_section)

    def transform_more_liners(self, original_spec, section_name, section_text):
        more_liners = filter(lambda x: not x[2], self.transformer_methods)
        skip_func = self.options['skip_functions']
        for func, pattern, _, sections in more_liners:
            if func.__name__ in skip_func:
                continue
            if section_name in sections and pattern.search(section_text):
                section_text = func(original_spec, pattern, section_text)

        return section_text

    def transform(self, original_spec, transformers=[]):
        """Initialize spec2scl.transformers and perform conversion
        by each subtransformer.
        Returns:
            converted spec file as a Specfile object
        """
        spec = specfile.Specfile(original_spec)
        import spec2scl.transformers
        self.subtransformers = transformers or map(
            lambda c: c(options=self.options), type(self).subtransformers)
        for subtrans in self.subtransformers:
            spec = subtrans._transform(original_spec, spec)

        spec.sections = [
            (section[0], self.merge_sclized_commands(section[1]))
            for section in spec.sections]

        return spec

    def _transform(self, original_spec, spec):
        for i, section in enumerate(spec.sections):
            spec.sections[i] = (
                section[0], self._transform_section(original_spec, section[0], section[1]))

        return spec

    def _transform_section(self, original_spec, section_name, section_text):
        section_text = self.transform_one_liners(
            original_spec, section_name, section_text)
        section_text = self.transform_more_liners(
            original_spec, section_name, section_text)

        return section_text

    # these methods are helpers for the actual transformations
    def get_original_name(self, original_spec):
        name_match = re.compile(r'Name:\s*([^\s]+)').search(original_spec)
        if name_match:
            return name_match.group(1)
        else:
            return 'TODO'

    def find_whole_commands(self, pattern, text):
        """Finds all matching commands, even if they are spread accross multiple lines.
        Args:
            pattern: re compiled pattern matching first line of the command
            text: string to match in
        Returns: list of strings, each of which is a whole command, in the exact form as it occurs in the specfile
        """
        # TODO: this is getting ugly, refactor
        commands = []

        while text:
            # find the matched string (usually beginning of command) inside text
            match = pattern.search(''.join(text))
            if not match:
                return commands

            # now use it to get the whole command
            previous_newline = text.rfind('\n', 0, match.start(0))
            # don't start from the matched pattern, but from the beginning of its line
            text = text[previous_newline + 1:]
            whole_comamnd = []
            for line in text.splitlines(True):
                whole_comamnd.append(line)
                if not line.rstrip().endswith('\\'):
                    break

            command = ''.join(whole_comamnd)
            # Do not sclize commented matches.
            comment_index = command.find('#')
            matched = match.group(0).rstrip()
            if comment_index == -1 or command.find(matched) < comment_index:
                commands.append(command)

            text = text[len(command):]

        return commands

    def sclize_one_command(self, command):
        return '{0}{1}{2}'.format(
            SCL_ENABLE,
            command if command.endswith('\n') else command + '\n',
            SCL_DISABLE
        )

    def sclize_all_commands(self, pattern, text):
        commands = self.find_whole_commands(pattern, text)
        # if there are multiple same commands, we only want to replace each once
        # => take only unique values by list(set())
        commands = list(set(commands))

        for command in commands:
            text = text.replace(command, self.sclize_one_command(command))

        return text

    def merge_sclized_commands(self, text):
        """Merge subsequent sclized commands into one sclized section."""
        return ''.join(text.split(SCL_DISABLE + SCL_ENABLE))


class MetaTransformer(object):

    """Class MetaTransformer provides necessary informations to create a
    specfile for metapackage
    """

    def __init__(self, meta_name, variables=None):
        self._meta_name = meta_name
        self._variables = variables

    def format_variables(self):
        """This function is used to separate given variables into dictionary

        Returns:
            Dictionary with variables names as keys and values as values
        """
        if self._variables:
            variables = self._variables.split(',')
            return dict([var.split('=') for var in variables])
        return {}

    def format_meta_name(self):
        """This function is used to separate version number from
        meta name of the package

        Returns:
            Tuple which consists of (meta_name, version)
        """
        r = re.compile('(.*?)([0-9]+)$')
        m = r.match(self._meta_name)
        return (m.group(1).lower(), m.group(2))

    @property
    def meta_name(self):
        try:
            return self.format_meta_name()[0]
        except(AttributeError):
            return self._meta_name  # If user enters meta package name in wrong format without version number at the end

    @property
    def meta_version(self):
        try:
            return self.format_meta_name()[1]
        except(AttributeError):
            return '2014'  # If user enters meta package name in wrong format without version number at the end

    @property
    def variables(self):
        return self.format_variables()

    @property
    def packager_data(self):
        try:
            packager_name = subprocess.Popen(
                'rpmdev-packager', stdout=subprocess.PIPE).communicate()[0].strip()
        except OSError:
            # Hi John Doe, you should install rpmdevtools
            packager_name = "John Doe <john@doe.com>"
        date_str = time.strftime('%a %b %d %Y', time.gmtime())
        encoding = locale.getpreferredencoding()
        return '{0} {1}'.format(date_str, packager_name.decode(encoding))
