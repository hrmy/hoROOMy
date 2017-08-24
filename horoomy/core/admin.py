from django.contrib import admin
from .models import *


@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = ('flat', 'complete', 'type', 'parser', 'created')


@admin.register(Contacts)
class ContactsAdmin(admin.ModelAdmin):
    list_display = ('phone', 'name')


@admin.register(Flat)
class FlatAdmin(admin.ModelAdmin):
    list_display = ('location', 'type', 'cost', 'area', 'rooms')


admin.site.register(Location)
admin.site.register(Metro)
admin.site.register(Image)
