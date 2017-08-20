from django.contrib import admin
from .tasks import parser_tasks
from .models import *


def start_parser(modeladmin, request, queryset):
    for parser in queryset:
        task_name = 'parsers.' + parser.name
        parser_tasks[task_name].delay()

start_parser.short_description = 'Запустить выбранные парсеры'


class ParserAdmin(admin.ModelAdmin):
    actions = [start_parser]


admin.site.register(Parser, ParserAdmin)