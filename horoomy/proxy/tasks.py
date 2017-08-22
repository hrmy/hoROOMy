from horoomy.utils.models import table_exists
from horoomy.utils.loader import load_package
from horoomy.parsers.models import Parser
from annoying.functions import get_object_or_None
from .utils import wrap
from . import sites


# Проверка на существование таблицы в БД
if table_exists('parsers_parser'):
    for name, task in load_package(sites, 'parse', wrap):
        # TODO: FIX PARSER MODEL
        if get_object_or_None(Parser, name=name) is None:
            Parser.objects.create(name=name)