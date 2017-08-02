# Подготавливаем здесь все, что будет нужно парсерам...
import requests
import re
import json
import time
import base64
import datetime
import threading
from bs4 import BeautifulSoup
from time import gmtime, strftime
from datetime import datetime, timedelta
# from parser_class import Parse
from datetime import date as datetimedate
# from driveAPI import BackuppedFile, upload_db
from botAPI import alertExc, tgExcCatch, alertBot, tgExcnoargs

__all__ = ['requests']  # ... и прописываем в __all__

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

# Это потом будем импортировать из других модулей
tasks = {}
# Идем по модулям в пакете
for _, name, _ in iter_modules(__path__):
    # Аналогично from . import <name>
    module = getattr(__import__('sites.' + name), name) 
    # Проверяем, есть ли там функция parse
    if not hasattr(module, 'parse'): continue
    # Проверяем наличие конфига
    
    tasks[name] = wrap(module.parse, name)