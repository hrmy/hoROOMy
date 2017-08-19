from django.contrib import admin
from .models import User, SocialNetworks


# Инлайн для отображения на странице редактирования юзера
class SocialNetworksInline(admin.StackedInline):
    model = SocialNetworks


# Админка для кастомной модельки юзера
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['name', 'second_name', 'email', 'date_joined', 'role', 'is_active']
    fields = ['name', 'second_name', 'email', 'role', 'phone', 'is_active', 'vn_action']
    inlines = (SocialNetworksInline,)


admin.site.register(User, CustomUserAdmin)
admin.site.register(SocialNetworks)
