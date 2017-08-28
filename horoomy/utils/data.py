import re


trim = lambda s: ' '.join(filter(None, re.split('\s', s)))
fullstrip = lambda s: re.sub('\s', '', s)


def dfilter(d, nested=True):
    d = dict(filter(lambda x: x[1] is not None, d.items()))
    if nested:
        for k, v in d.items():
            if isinstance(v, dict):
                d[k] = dfilter(v)
    return d


def cast(func, value, default=None):
    try:
        return func(value)
    except:
        return default