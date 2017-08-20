def trim(s):
    if not s or not isinstance(s, str): return ''
    words = filter(None, re.split('\s', s))
    return ' '.join(words)


def try_default(func, value, default=None):
    try:
        return func(value)
    except:
        return default