from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from expensesapp.models import User, Claim


class ClaimAdmin(admin.ModelAdmin):
    list_display = ("creation_datetime", "owner", "description")


admin.site.register(Claim, ClaimAdmin)
admin.site.register(User, UserAdmin)