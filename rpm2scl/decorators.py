import re

def matches(pattern, one_line = True, flags = 0):
    def inner(func):
        func.one_line = one_line
        if not hasattr(func, 'matches'):
            func.matches = [re.compile(pattern)]
        else:
            func.matches.append(re.compile(pattern))
        return func

    return inner
