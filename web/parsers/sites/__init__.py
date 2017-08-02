# Подготавливаем все, что будет нужно парсерам
import requests

# Прописываем в __all__
__all__ = ['requests']

# А вот здесь заведем обертку на парсеры
from functools import wraps

# Сама обертка
def wrap(func, name):
    @wraps(func)
    def deco(**kwargs):
        config = ParserConfig.objects.get(name=name)
        raw_data = func(**config.to_dict())
        objects = [Flat(**i) for i in raw_data]
        Flat.objects.bulk_create(objects)

    return deco
    
# Ну и это для меня
from pkgutil import iter_modules

sites = {}
for _, name, __ in iter_modules(__path__):
    module = getattr(__import__('sites.' + name), name)  # Аналогично from . import <name>
    if not hasattr(module, 'parse'): continue
    sites[name] = wrap(module.parse, name)