from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Отоброжение модели в интерфейсе"""
    list_display = ("username", "email", "first_name", "last_name")
    search_fields = ("username", "email")
    list_filter = ("username", "email")
    ordering = ("username",)
