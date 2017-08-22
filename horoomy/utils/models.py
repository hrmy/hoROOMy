from django.utils.text import slugify
from django.db import connection


# Упрощенная и подпиленная версия Choices из либы django-model-utils
class Choices:
    def __init__(self, *values):
        self.choices = {}
        for i, value in enumerate(values):
            db_value = str(i)
            const_value = value
            if isinstance(value, tuple):
                const_value, value = value
            self.choices[db_value] = value
            attr = slugify(const_value).upper()
            setattr(self, attr, db_value)

    def __iter__(self):
        items = sorted(self.choices.items(), key=lambda x: x[0])
        for i in items: yield i

    def __getitem__(self, item):
        return self.choices[item]


# Существует ли таблица в базе данных
def table_exists(name):
    return name in connection.introspection.table_names()
