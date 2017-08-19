# Horoomy - Housing as a Service

## Стек технологий
- Python 3.6
- Django 1.11
- PostgreSQL
- Redis
- Celery

## Хостинг
Хостинг проекта осуществляется на [Heroku](https://heroku.com/)  
Рабочая версия сайта: [horoomy-webapp.herokuapp.com](https://horoomy-webapp.herokuapp.com/)  
Аккаунт от [админки](https://horoomy-webapp.herokuapp.com/admin/): `horoomy2017@gmail.com:horoomy-admin`

## Структура проекта
- В папке `config` находятся все файлы, связанные с конфигурацией проекта
  - `requirements` - список необходимых Python-пакетов
  - `settings` - настройки Django-проекта
  - `urls.py` - базовые URL сайта
  - `wsgi.py` - инициализация WSGI
  - `celery.py` - инициализация Celery
- В папке `horoomy` - Django-приложения, шаблоны и статические файлы

Конфигурация в папках `requirements` и `settings` разбита на 3 файла: общая (`base`), для разработки (`dev`) и для деплоя (`pro`)

### Что нового
- PostgreSQL теперь используется не только для деплоя, но и для разработки
- Убран костыль для `manage.py`, выбирающий нужные настройки в зависимости от введенных команд
- Упорядочены настройки Django-проекта (`base.py`)
- В связи с изменением структуры проекта, кастомные Django-приложения теперь следует прописывать с префиксом `horoomy.`
- Кое-какие настройки теперь подтягиваются из переменных окружения (см. ниже)
- Все операции записи в БД во вьюхах теперь выполняются одной транзакцией

## Запуск проекта на локальной машине

### Подготовка

1. Установить нужную версию Python
2. Рекомндуется: установить virtualenvwrapper (или virtualenvwrapper-win) и [настроить](http://docs.python-guide.org/en/latest/dev/virtualenvs/) его
3. Установить нужные Python-пакеты:
```
pip install -r config/requirements/dev.txt
```
4. Установить PostgreSQL и [настроить](https://djbook.ru/examples/77/) ее
5. Настроить переменные окружения:
```
DJANGO_SETTINGS_MODULE = 'config.settings.dev'
DATABASE_URL = 'postgres://USER:PASSWORD@HOST:PORT/NAME'
Опционально:
DEBUG = True / False (по умолчанию True)
DJANGO_EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```
6. По желанию вынести настройку переменных окружения в postactivate/postdeactivate скрипты virtualenv
7. Выполнить команды `manage.py`:
```
python manage.py makemigrations (только при необходимости)
python manage.py migrate
python manage.py createsuperuser
```

### Запуск

1. Запустить сервер PostgreSQL
2. Запустить Celery-beat и Celery-worker:
```
python manage.py celery beat --app=config.celery.app
python manage.py celery worker --app=config.celery.app
```
3. Запустить web-сервер:
```
python manage.py runserver 80
```