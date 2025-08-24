from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ("id", "email", "is_staff", "is_active", "timezone")
    ordering = ("email",)
    fieldsets = (
        (None, {"fields": ("email", "password", "timezone")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "timezone", "is_staff", "is_active"),
        }),
    )
    search_fields = ("email",)
    