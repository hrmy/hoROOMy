# Подготавливаем здесь все, что будет нужно парсерам...
import re
import json
import time
import base64
from bs4 import BeautifulSoup
from time import gmtime, strftime, strptime
from datetime import datetime, timedelta
from datetime import date as datetimedate
from horoomy.proxy import wrapper as requests

# ... и прописываем в __all__
__all__ = [
    'requests',
    'json',
    'time',
    'base64',
    'datetime',
    'BeautifulSoup',
    'gmtime',
    'strftime',
    'strptime',
    'datetimedate',
    'timedelta',
    're'
]

from horoomy.utils.loader import load_all_modules

# Без понятия как это работает
load_all_modules(__package__, __path__)