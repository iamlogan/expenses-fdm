from django.contrib import admin
from expensesapp.models import Claim, Receipt


class ClaimAdmin (admin.ModelAdmin):
    list_display = ("creation_datetime", "owner",)


admin.site.register(Claim, ClaimAdmin)