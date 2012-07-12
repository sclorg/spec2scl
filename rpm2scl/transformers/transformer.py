import re

class Transformer(object):
    def __init__(self, spec, options = None):
        self.original_spec = spec
        self.scl_spec = spec
        self.options = options or {}
        self.one_line_transformers, self.more_lines_transformers = self.collect_transformer_methods()

    def collect_transformer_methods(self):
        one_line = {}
        more_lines = {}

        for attr in self.__class__.__dict__:
            try:
                matches = getattr(getattr(self, attr), 'matches')
                if getattr(getattr(self, attr), 'one_line'):
                    one_line[getattr(self, attr)] = matches
                else:
                    more_lines[getattr(self, attr)] = matches
            except: # doesn't have matches attribute
                pass

        return (one_line, more_lines)

    def apply_one_line_transformers(self):
        split_spec = self.scl_spec.splitlines()
        for index, line in enumerate(split_spec):
            for one_line_transformer, patterns in self.one_line_transformers.items():
                for pattern in patterns:
                    if pattern.search(line):
                        # let all the patterns modify the line
                        line = one_line_transformer(pattern, line)
            split_spec[index] = line

        return '\n'.join(split_spec)

    def apply_more_line_transformers(self):
        temp_spec = self.scl_spec
        for more_lines_transformer, patterns in self.more_lines_transformers.items():
            for pattern in patterns:
                if pattern.search(temp_spec):
                    temp_spec = more_lines_transformer(pattern, temp_spec)

        return temp_spec

    def transform(self):
        for subcls in type(self).__subclasses__():
            obj = subcls(self.scl_spec, self.options)
            self.scl_spec = obj._transform()

        return self.scl_spec

    def _transform(self):
        self.scl_spec = self.apply_one_line_transformers()
        self.scl_spec = self.apply_more_line_transformers()

        return self.scl_spec

    # these methods are helpers for the actual transformations
    def get_original_name(self):
        name_match = re.compile(r'Name:\s*([^\s]+)').search(self.original_spec)
        if name_match:
            return name_match.group(0)
        else:
            return 'TODO'

    def find_whole_command(self, pattern, text):
        """Finds whole command, even if it is spread accross multiple lines.
        Args:
            pattern: re compiled pattern matching first line of the command
            text: string to match in
        Returns: the whole command as a string
        """
        whole_command = []
        # find the matched string (usually beginning of command) inside text
        matched = pattern.search(text).group(0)
        # now use it to get the whole command
        append = False
        for line in text.splitlines():
            if line.find(matched) != -1:
                append = True
            if append:
                whole_command.append(line)
            if append and not line.rstrip().endswith('\\'):
                break # sorry :)

        whole_command.append('') # so that we don't loose the last newline when joining

        return '\n'.join(whole_command)

    def sclize_whole_command(self, pattern, text):
        command = self.find_whole_command(pattern, text)
        new_command = [None] * 3
        new_command[1] = command
        if self.command_needs_heredoc_for_execution(command):
            new_command[0] = '%{?scl:scl enable %{scl} - << \EOF}\n'
            new_command[2] = '%{?scl:EOF}\n'
        else:
            quotes_type = "'" if command.find('"') != -1 else '"'
            new_command[0] = '%{{?scl:scl enable %{{scl}} {0}}}\n'.format(quotes_type)
            new_command[2] = '%{{?scl:{0}}}\n'.format(quotes_type)

        return text.replace(command, ''.join(new_command))

    def command_needs_heredoc_for_execution(self, command):
        shell_var_assignment_re = re.compile(r'^\s*\w+=', re.MULTILINE)
        contains_shell_var_assignment = shell_var_assignment_re.search(command)

        return contains_shell_var_assignment
