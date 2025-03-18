from django.urls import path, include

urlpatterns = [
    path("xero/", include("features.xero.urls")),
    path("rest-auth/", include("rest_framework.urls")),
]
