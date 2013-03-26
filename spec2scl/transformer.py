import re

from spec2scl import specfile

class Transformer(object):
    def __init__(self, options={}):
        self.options = options
        self.subtransformers = list(map(lambda x: x(self.options), type(self).__subclasses__()))
        self.transformer_methods = self.collect_transformer_methods()

    def collect_transformer_methods(self):
        transformers = []

        for v in vars(type(self)).values():
            if hasattr(v, 'matches'):
                for i in range(len(v.matches)):
                    transformers.append((getattr(self, v.__name__), v.matches[i], v.one_line[i], v.sections[i]))

        return transformers

    def transform_one_liners(self, original_spec, section_name, section_text):
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
        more_liners = filter(lambda x: not x[2], self.transformer_methods)
        for func, pattern, _, sections in more_liners:
            if section_name in sections and pattern.search(section_text):
                section_text = func(original_spec, pattern, section_text)

        return section_text

    def transform(self, original_spec):
        spec = specfile.Specfile(original_spec)
        for subtrans in self.subtransformers:
            spec = subtrans._transform(original_spec, spec)

        return spec

    def _transform(self, original_spec, spec):
        for i, section in enumerate(spec.sections):
            spec.sections[i] = (section[0], self._transform_section(original_spec, section[0], section[1]))

        return spec

    def _transform_section(self, original_spec, section_name, section_text):
        section_text = self.transform_one_liners(original_spec, section_name, section_text)
        section_text = self.transform_more_liners(original_spec, section_name, section_text)

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
        while(True):
            # find the matched string (usually beginning of command) inside text
            match = pattern.search(''.join(text))
            if not match:
                break
            matched = match.group(0)
            if matched.endswith('\n'):
                # if matched ends with newline, then we might have got e.g.
                # 'make\n\n', but that will not work because we are splitting
                # lines below, so we can only match one newline at the end
                matched = matched.rstrip('\n') + '\n'

            append = False
            whole_command = []
            # now use it to get the whole command
            index = match.start(0)
            previous_newline = text.rfind('\n', 0, index)
            # don't start from the matched pattern, but from the beginning of its line
            text = text[previous_newline if previous_newline != -1 else 0:]
            for line in text.splitlines(True):
                if line.find(matched) != -1:
                    append = True
                if append:
                    whole_command.append(line)
                if append and not line.rstrip().endswith('\\'):
                    break # sorry :)

            command = ''.join(whole_command)
            text = text[len(command):] # so that we don't find it again
            comment_index = command.find('#')
            # only append if not matched
            if comment_index == -1 or command.find(matched) < comment_index:
                commands.append(command)

        return commands

    def sclize_one_command(self, command):
        new_command = [None] * 3
        new_command[1] = command

        if self.command_needs_heredoc_for_execution(command):
            new_command[0] = '%{?scl:scl enable %{scl} - << \EOF}\n'
            new_command[2] = '%{?scl:EOF}\n'
        else:
            quotes_type = "'" if command.find('"') != -1 else '"'
            new_command[0] = '%{{?scl:scl enable %{{scl}} {0}}}\n'.format(quotes_type)
            new_command[2] = '%{{?scl:{0}}}\n'.format(quotes_type)

        return ''.join(new_command)

    def sclize_all_commands(self, pattern, text):
        commands = self.find_whole_commands(pattern, text)
        # if there are multiple same commands, we only want to replace each once => take only unique values by list(set())
        commands = list(set(commands))

        for command in commands:
            text = text.replace(command, self.sclize_one_command(command))

        return text

    def command_needs_heredoc_for_execution(self, command):
        """Returns true if the command needs heredoc for execution
        Args:
            command: string containing the whole command
        Returns:
            True if heredoc is needed (contains both single and double quotes or var assignment),
            False otherwise
        """
        single_quotes = command.find("'")
        double_quotes = command.find('"')

        shell_var_assignment_re = re.compile(r'^\s*\w+=', re.MULTILINE)
        contains_shell_var_assignment = shell_var_assignment_re.search(command)

        return  True if contains_shell_var_assignment or (single_quotes != -1 and double_quotes != -1) else False
