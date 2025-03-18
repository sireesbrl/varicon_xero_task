from django.urls import path
from .views import (
    XeroLoginAPIView,
    XeroCallbackAPIView,
    RefreshTokenAPIView,
    UpdateChartOfAccountsAPIView,
    ChartOfAccountsAllAPIView,
)

urlpatterns = [
    path("login/", XeroLoginAPIView.as_view(), name="xero-login"),
    path("callback/", XeroCallbackAPIView.as_view(), name="xero-callback"),
    path("refresh/", RefreshTokenAPIView.as_view(), name="xero-refresh-token"),
    path(
        "accounts/update/",
        UpdateChartOfAccountsAPIView.as_view(),
        name="xero-accounts-update"
    ),
    path(
        "accounts/all/",
        ChartOfAccountsAllAPIView.as_view(),
        name="xero-accounts-all"
    ),
]
