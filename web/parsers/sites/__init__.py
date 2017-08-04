# Подготавливаем здесь все, что будет нужно парсерам...
from . import randomproxy as requests
import re
import json
import time
import base64
from bs4 import BeautifulSoup
from time import gmtime, strftime, strptime
from datetime import datetime, timedelta
from datetime import date as datetimedate

__all__ = ['requests', 'json', 'time', 'base64', 'datetime', 'BeautifulSoup', 'gmtime',
           'strftime', 'strptime', 'datetimedate', 'timedelta', 're']  # ... и прописываем в __all__

# Подготавливаем таски, заодно создавая несуществующие конфиги
from pkgutil import iter_modules
from celery import shared_task
from annoying.functions import get_object_or_None
from ..models import *
from .utils import wrap

# Это потом будем импортировать из других модулей
tasks = {}
# Идем по модулям в пакете
for _, name, _ in iter_modules(__path__):
    # Аналогично from . import <name>
    module = getattr(__import__(__package__, fromlist=[name]), name)
    # Проверяем, есть ли там функция parse
    if not hasattr(module, 'parse'): continue
    # Проверяем наличие конфига и создаем таск
    task_name = 'parsers.' + name
    tasks[task_name] = shared_task(name=task_name)(wrap(module.parse, name))
    #if get_object_or_None(Parser, name=name) is None:
    #    Parser.objects.create(name=name)