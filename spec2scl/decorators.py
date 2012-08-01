import re

def matches(pattern, one_line = True, flags = 0):
    if one_line:
        flags = 0
    else:
        flags = re.MULTILINE

    def inner(func):
        func.one_line = one_line
        if not hasattr(func, 'matches'):
            func.matches = [re.compile(pattern, flags)]
        else:
            func.matches.append(re.compile(pattern, flags))
        return func

    return inner
