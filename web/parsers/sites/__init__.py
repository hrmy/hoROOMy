# Подготавливаем здесь все, что будет нужно парсерам...
import requests
import re
import json
import time
import base64
import datetime
from bs4 import BeautifulSoup
from time import gmtime, strftime
from datetime import datetime, timedelta
from datetime import date as datetimedate
from utils import alertExc, json_check

__all__ = ['requests', 'json', 'time', 'base64', 'datetime', 'BeautifulSoup', 'gmtime',
           'strftime', 'datetimedate', 'timedelta', 'alertExc', 're', 'json_check']  # ... и прописываем в __all__

# Обертка на парсеры
def wrap(func, name):
    # Конкретно *эта* функция будет вызываться в качестве Celery-таска
    def deco():
        # Получаем конфиг для парсера
        config = Parser.objects.get(name=name).get_config()
        # Запускаем саму функцию, она должна вернуть итератор по словарям
        raw_data = func(**config)
        # Создаем объекты БД из полученных словарей (пока не пушим)
        objects = [Flat(**i) for i in raw_data]
        # Разом запихиваем все объекты в БД (спасибо bulk_create)
        Flat.objects.bulk_create(objects)

    deco.__name__ = 'parse_' + name

    return deco

# Подготавливаем таски, заодно создавая несуществующие конфиги
from pkgutil import iter_modules
from celery import shared_task
from annoying.functions import get_object_or_None
from ..models import *

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
    if get_object_or_None(Parser, name=name) is None:
        print('Created parser object with name {}'.format(name))
        Parser.objects.create(name=name)