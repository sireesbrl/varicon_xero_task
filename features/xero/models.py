from django.db import models

class XeroToken(models.Model):
    access_token = models.TextField()
    refresh_token = models.TextField()
    expires_in = models.IntegerField()

    def __str__(self):
        return f"Token expires in {self.expires_in} seconds"

    class Meta:
        verbose_name = "Xero Token"
        verbose_name_plural = "Xero Tokens"

class ChartOfAccount(models.Model):
    account_id = models.UUIDField(primary_key=True)
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=100)
    bank_account_number = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=20, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    bank_account_type = models.CharField(max_length=50, null=True, blank=True)
    currency_code = models.CharField(max_length=10, null=True, blank=True)
    tax_type = models.CharField(max_length=50, null=True, blank=True)
    enable_payments_to_account = models.BooleanField(default=False)
    show_in_expense_claims = models.BooleanField(default=False)
    class_type = models.CharField(max_length=50, null=True, blank=True)
    system_account = models.CharField(max_length=50, null=True, blank=True)
    reporting_code = models.CharField(max_length=50, null=True, blank=True)
    reporting_code_name = models.CharField(max_length=255, null=True, blank=True)
    has_attachments = models.BooleanField(default=False)
    updated_date_utc = models.DateTimeField(null=True, blank=True)
    add_to_watchlist = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        verbose_name = "Chart of Account"
        verbose_name_plural = "Chart of Accounts"
        ordering = ["name"]