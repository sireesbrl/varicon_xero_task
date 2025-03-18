from django.contrib import admin
from features.users.models import BaseUser

@admin.register(BaseUser)
class BaseUserAdmin(admin.ModelAdmin):
    list_display = ["email", "first_name", "last_name", "is_active", "is_admin"]