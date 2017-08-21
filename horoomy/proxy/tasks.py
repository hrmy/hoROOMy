from horoomy.utils.loader import load_package
from horoomy.parsers.models import Parser
from annoying.functions import get_object_or_None
from . import sites


parser_tasks = {}

# Проверка на существование таблицы в БД
try:
    list(Parser.objects.all())
except:
    pass
else:
    for name, task in load_package(sites, 'parse', sites.utils.wrap):
        parser_tasks[task.name] = task
        # TODO: FIX PARSER MODEL
        if get_object_or_None(Parser, name=task.name) is None:
            Parser.objects.create(name=task.name)