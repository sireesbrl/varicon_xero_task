from django.contrib import admin
from features.xero.models import XeroToken, ChartOfAccount

@admin.register(XeroToken)
class XeroTokenAdmin(admin.ModelAdmin):
    pass

@admin.register(ChartOfAccount)
class ChartOfAccountAdmin(admin.ModelAdmin):
    list_display = ["account_id", "code", "name", "type", "status"]
