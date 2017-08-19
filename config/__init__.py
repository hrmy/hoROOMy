# Заранее загружаем Celery-app для использования в других модулях
from .celery import app as celery_app
