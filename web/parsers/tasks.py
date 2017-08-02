from .sites import sites
from celery import shared_task


for name, func in sites.items():
    shared_task(name='Parse ' + name)(func)