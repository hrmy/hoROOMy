from django.contrib import admin
from django.contrib.auth import get_user_model


# Админка для кастомной модельки юзера
# Добавьте при случае в fields все что нужно
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'date_joined', 'is_active']
    fields = ['name', 'email', 'phone', 'is_active', 'vn_action']

admin.site.register(get_user_model(), CustomUserAdmin)