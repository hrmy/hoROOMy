# Подготавливаем все, что будет нужно парсерам
import requests

# Прописываем в __all__
__all__ = ['requests']

# А вот здесь заведем обертку на парсеры
from functools import wraps
# Здесь будет наша моделька (эта для примера)
from django.contrib.auth.models import User

# Сама обертка
def wrap(func):
    @wraps(func)
    def deco(**kwargs):
        raw_data = func(**kwargs)
        for i in raw_data: User.objects.create(**i)

    return deco
    
# Ну и это для меня
from pkgutil import iter_modules

sites = {}
for _, name, __ in iter_modules(__path__):
    parse_func = getattr(__import__('sites.' + name), name).parse
    sites[name] = wrap(parse_func)