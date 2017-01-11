import re

from spec2scl import settings


def matches(pattern, one_line=True, sections=settings.RUNTIME_SECTIONS, flags=0):
    """Convert the provided arguments into attributes of the function object,
    which are further processed by the base transformer class.
    """
    if not one_line:
        flags = re.MULTILINE

    def inner(func):
        if not hasattr(func, 'matches'):
            func.one_line = [one_line]
            func.matches = [re.compile(pattern, flags)]
            func.sections = [sections]
        else:
            func.one_line.append(one_line)
            func.matches.append(re.compile(pattern, flags))
            func.sections.append(sections)
        return func

    return inner
