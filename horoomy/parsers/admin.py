from django.contrib import admin
from celery import current_app
from .models import *


def start_parser(modeladmin, request, queryset):
    for parser in queryset:
        # TODO: FIX THAT SHIT
        current_app.send_task('parse.' + parser.name.lower())


start_parser.short_description = 'Запустить выбранные парсеры'


class ParserAdmin(admin.ModelAdmin):
    actions = [start_parser]


admin.site.register(Parser, ParserAdmin)

# TODO: FIX
from . import tasks
