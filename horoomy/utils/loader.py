from pkgutil import iter_modules


def load_all_modules(package, path):
    for _, name, _ in iter_modules(path):
        # Аналогично from . import <name>
        module = getattr(__import__(package, fromlist=[name]), name)


def load_package(package, search, wrapper=None):
    funcs = []
    for name, module in package.__dict__.items():
        if name.startswith('__'): continue
        if not hasattr(module, '__package__'): continue
        if module.__package__ != package.__package__: continue
        if hasattr(module, search):
            func = getattr(module, search)
            if wrapper is not None: func = wrapper(func, name=name)
            funcs.append((name, func))
    return funcs