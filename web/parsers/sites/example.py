from . import *

# На самом деле метод должен называться parse
def parse_(**kwargs):
    logger = kwargs['logger']  # Гарантируется
    logger.name = 'Whatever'
    
    # Stuff...
    
    # Примеры использования логгера:
    logger.info('All\'s ok')
    logger.warning('Not so ok')
    logger.error('Absolutely not ok')
    # Также можно замерять время
    logger.timestamp('timestamp_name')
    # ...
    delta = logger.timestamp('timestamp_name')
    logger.info('Succeed in {} seconds'.format(delta.seconds))
    # Проверять ключи словарей (name=... нужен только для отображения названия словаря - не обязателен)
    strange_dict = {}
    logger.check_keys(strange_dict, 'key1', 'key2', 'key3', name='strange_dict')
    # Или проверять условия
    success = False
    logger.check(success, name='All is ok')
    
    # Возвращать, как договорились, генератор
    for i in my_data: yield i
    
    # При желании можно бросаться - все перехватывается
    raise Exception('FATAL ERROR')