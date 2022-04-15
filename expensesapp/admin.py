from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib import admin
from expensesapp.models import *


@admin.register(Currency)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ("name", "iso_code", "symbol", "vat_name")


class TeamMemberInline(admin.TabularInline):
    model = get_user_model()
    verbose_name_plural = "Team Members"
    fields = ["first_name", "last_name", "email"]
    readonly_fields = ["first_name", "last_name", "email"]
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    # Define admin model for custom User model with no email field

    fieldsets = (
        (None, {"fields": ("email", "first_name", "last_name", "password")}),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser",
                                       "groups", "user_permissions")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
        (_("Preferences"), {"fields": ("default_currency",)}),
        (_("Hierarchy"), {"fields": ("primary_manager",)}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2"),
        }),
    )
    list_display = ("display_name", "first_name", "last_name", "email", "is_staff", "last_login")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)

    @admin.display()
    def display_name(self, obj):
        return str(obj)

    inlines = [TeamMemberInline]


@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ("owner", "currency", "reference", "creation_datetime", "description", "status")


@admin.register(Category)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ("owner", "claim", "category", "reference", "creation_datetime", "date_incurred", "amount", "vat",
                    "description")

    @admin.display()
    def owner(self, obj):
        return obj.claim.owner
