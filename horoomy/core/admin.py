from django.contrib import admin
from .models import *


@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'complete', 'type', 'parser', 'created')


admin.site.register(Location)
admin.site.register(Metro)
admin.site.register(Flat)
admin.site.register(Contacts)
admin.site.register(Image)
