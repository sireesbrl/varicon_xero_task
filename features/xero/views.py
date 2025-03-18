from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import redirect
from config.env import env
import requests
from .models import XeroToken, ChartOfAccount
from .serializers import ChartOfAccountSerializer

XERO_AUTH_URL = "https://login.xero.com/identity/connect/authorize"
XERO_TOKEN_URL = "https://identity.xero.com/connect/token"
XERO_ACCOUNTS_URL = "https://api.xero.com/api.xro/2.0/Accounts"

class XeroLoginAPIView(APIView):
    """
    Get a redirect URL for Xero OAuth authorization.

    Returns a redirect URL for the Xero OAuth authorization flow.
    The URL includes the client ID, redirect URI, and scope.

    Returns:
        Response: A response object containing the redirect URL.
    """
    def get(self, request):
        params = {
            "response_type": "code",
            "client_id": env.str("XERO_CLIENT_ID"),
            "redirect_uri": env.str("XERO_REDIRECT_URI"),
            "scope": "accounting.settings.read offline_access",
        }
        auth_url = f"{XERO_AUTH_URL}?"+ "&".join([f"{k}={v}" for k, v in params.items()])
        return Response({"redirect_url": auth_url}, status=status.HTTP_200_OK)


class XeroCallbackAPIView(APIView):
    """
    Handle the Xero authorization code callback.

    This view handles the authorization code callback from Xero after the user
    has authorized the app. It exchanges the authorization code for an access
    token and refresh token, and stores them in the database.

    Returns:
        Response: A response object containing the result of the authentication
        flow.
    """
    def get(self, request):
        code = request.GET.get("code")
        if not code:
            return Response({"error": "Authorization code missing"}, status=status.HTTP_400_BAD_REQUEST)

        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": env.str("XERO_REDIRECT_URI"),
            "client_id": env.str("XERO_CLIENT_ID"),
            "client_secret": env.str("XERO_CLIENT_SECRET"),
        }
        response = requests.post(XERO_TOKEN_URL, data=data).json()

        if "error" in response:
            return Response({"error": response.get("error_description", "OAuth token exchange failed")}, status=status.HTTP_400_BAD_REQUEST)

        XeroToken.objects.update_or_create(
            id=1,
            defaults={
                "access_token": response["access_token"],
                "refresh_token": response["refresh_token"],
                "expires_in": response["expires_in"],
            },
        )
        return Response({"message": "Xero authentication successful"}, status=status.HTTP_200_OK)

class RefreshTokenAPIView(APIView):
    """
    Retrieve and refresh the Xero access token using the stored refresh token.

    This method checks for the existence of a stored Xero token. If a token is found,
    it attempts to refresh the access token by making a POST request to the Xero
    identity API using the stored refresh token and client credentials. If successful,
    it updates the token information in the database and returns a success message
    with the new access token. If the refresh fails, it returns an error message
    with details of the failure.

    Args:
        request: The HTTP request object.

    Returns:
        Response: A Django Rest Framework Response object containing the result of
        the token refresh operation. On success, it includes the new access token.
        On failure, it includes error details.
    """
    def get(self, request):

        token = XeroToken.objects.first()
        if not token:
            return Response({"error": "No token found"}, status=status.HTTP_400_BAD_REQUEST)

        data = {
            "grant_type": "refresh_token",
            "refresh_token": token.refresh_token,
            "client_id": env.str("XERO_CLIENT_ID"),
            "client_secret": env.str("XERO_CLIENT_SECRET"),
        }

        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        response = requests.post("https://identity.xero.com/connect/token", data=data, headers=headers)
        response_data = response.json()

        if response.status_code == 200 and "access_token" in response_data:
            token.access_token = response_data["access_token"]
            token.refresh_token = response_data["refresh_token"]
            token.expires_in = response_data["expires_in"]
            token.save()

            return Response(
                {"message": "Token refreshed successfully", "access_token": token.access_token},
                status=status.HTTP_200_OK
            )

        return Response(
            {"error": "Token refresh failed", "details": response_data},
            status=status.HTTP_400_BAD_REQUEST
        )

class UpdateChartOfAccountsAPIView(APIView):
    """
    Retrieve a list of Chart of Accounts from Xero.

    This method checks for the existence of a stored Xero token. If a token is found,
    it makes a GET request to the Xero API to retrieve the list of Chart of Accounts.
    On success, it updates the Chart of Accounts in the database and returns a success
    message with the list of Chart of Accounts. If the request fails, it returns an error
    message with details of the failure.

    Args:
        request: The HTTP request object.

    Returns:
        Response: A Django Rest Framework Response object containing the result of
        the Chart of Accounts retrieval operation. On success, it includes the list of
        Chart of Accounts. On failure, it includes error details.
    """
    def get(self, request):
        token = XeroToken.objects.first()
        if not token:
            return Response({"error": "No token found"}, status=status.HTTP_400_BAD_REQUEST)

        headers = {
            "Authorization": f"Bearer {token.access_token}",
            "Accept": "application/json"
        }
        response = requests.get(XERO_ACCOUNTS_URL, headers=headers)

        if response.status_code == 401:
            return Response({"error": "Unauthorized - Token expired"}, status=status.HTTP_401_UNAUTHORIZED)

        data = response.json()

        accounts_data = []
        for account in data.get("Accounts", []):
            account_obj, created = ChartOfAccount.objects.update_or_create(
                account_id=account["AccountID"],
                defaults={
                    "code": account.get("Code"),
                    "name": account.get("Name"),
                    "type": account.get("Type"),
                    "bank_account_number": account.get("BankAccountNumber"),
                    "status": account.get("Status"),
                    "description": account.get("Description"),
                    "bank_account_type": account.get("BankAccountType"),
                    "currency_code": account.get("CurrencyCode"),
                    "tax_type": account.get("TaxType"),
                    "enable_payments_to_account": account.get("EnablePaymentsToAccount", False),
                    "show_in_expense_claims": account.get("ShowInExpenseClaims", False),
                    "class_type": account.get("Class"),
                    "system_account": account.get("SystemAccount"),
                    "reporting_code": account.get("ReportingCode"),
                    "reporting_code_name": account.get("ReportingCodeName"),
                    "has_attachments": account.get("HasAttachments", False),
                    "updated_date_utc": account.get("UpdatedDateUTC"),
                    "add_to_watchlist": account.get("AddToWatchlist", False),
                },
            )
            accounts_data.append(account_obj)

        serializer = ChartOfAccountSerializer(accounts_data, many=True)
        return Response({"message": "Chart of Accounts retrieved successfully", "data": serializer.data}, status=status.HTTP_200_OK)

class ChartOfAccountsAllAPIView(ListAPIView):
    """
    API endpoint to retrieve all Chart of Accounts.

    Returns a list of all Chart of Accounts from Xero.
    """
    queryset = ChartOfAccount.objects.all()
    serializer_class = ChartOfAccountSerializer
