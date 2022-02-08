from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib import admin
from expensesapp.models import User, Claim


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    # Define admin model for custom User model with no email field

    fieldsets = (
        (None, {"fields": ("email", "first_name", "last_name", "password")}),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser",
                                       "groups", "user_permissions")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2"),
        }),
    )
    list_display = ("email", "first_name", "last_name", "is_staff", "last_login")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)


class ClaimAdmin(admin.ModelAdmin):
    list_display = ("creation_datetime", "owner", "description")


admin.site.register(Claim, ClaimAdmin)
