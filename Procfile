web: gunicorn config.wsgi --log-file -
beat: celery beat --app=config.celery.app
worker: celery worker --app=config.celery.app
