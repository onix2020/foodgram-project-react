from django.contrib.admin import register
from django.contrib.auth.admin import UserAdmin

from .models import MyUser


@register(MyUser)
class MyUserAdmin(UserAdmin):
    list_display = (
        'username', 'first_name', 'last_name', 'email', 'active',
    )
    fields = (
        ('username', 'email', ),
        ('first_name', 'last_name', ),
        ('active',),
    )
    fieldsets = []

    search_fields = (
        'username', 'email', 'active',
    )
    list_filter = (
        'first_name', 'email', 'active',
    )
    save_on_top = True
