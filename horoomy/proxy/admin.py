from django.contrib import admin
from .models import *

admin.site.register(Proxy)
admin.site.register(UserAgent)

# TODO: FIX
from . import tasks
