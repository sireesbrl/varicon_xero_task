from rest_framework.test import APITestCase
from rest_framework import status
from features.xero.models import ChartOfAccount, XeroToken
from features.xero.serializers import ChartOfAccountSerializer
from unittest.mock import patch
import uuid

class XeroLoginAPIViewTests(APITestCase):
    def setUp(self):
        """
        Set up the test by defining the URL of the XeroLoginAPIView.
        """
        self.url = "/api/v1/xero/login/"

    def test_get_redirect_url(self):
        """
        Test that the API returns a redirect URL for Xero OAuth authorization.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("https://login.xero.com/identity/connect/authorize", response.data["redirect_url"])

class XeroCallbackAPIViewTests(APITestCase):
    def setUp(self):
        """
        Set up the test by defining the URL of the XeroCallbackAPIView.
        """
        self.url = "/api/v1/xero/callback/"

    @patch("features.xero.views.requests.post")
    def test_get_tokens(self, mock_get):
        """
        Test that the API returns the Xero access token and refresh token.
        """
        mock_response = {
            "access_token": "mock_access_token",
            "refresh_token": "mock_refresh_token",
            "expires_in": 3600
        }
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        response = self.client.get(self.url, {"code": "mock_authorization_code"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Xero authentication successful")

    @patch("features.xero.views.requests.post")
    def test_missing_authorization_code(self, mock_post):
        """
        Test that the API returns an error response when the authorization code is missing.
        """
        mock_post.return_value.status_code = 400
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Authorization code missing")

class RefreshAccessTokenAPIViewTests(APITestCase):
    def setUp(self):
        """
        Set up the test by creating a valid Xero token in the database, and
        defining the URL of the RefreshAccessTokenAPIView.
        """
        self.token = XeroToken.objects.create(
            access_token="valid_access_token",
            refresh_token="valid_refresh_token",
            expires_in=3600,
        )
        self.url = "/api/v1/xero/token/refresh/"

    @patch("requests.post")
    def test_get(self, mock_post):
        """
        Test that the API returns a 200 status code when accessing the endpoint.
        """
        mock_response = {
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
            "expires_in": 3600
        }
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_response
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_token_refresh_failed(self):
        """
        Test that the API returns a 400 status code and an appropriate error message
        when the token is expired and needs to be refreshed.
        """

        self.token.expires_in = 0
        self.token.save()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Token refresh failed")

    def test_no_token_found(self):
        """
        Test that the API returns a 400 status code and an appropriate error message
        when there is no Xero token present in the database.
        """
        XeroToken.objects.all().delete()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "No token found")


class UpdateChartOfAccountsAPIViewTests(APITestCase):
    def setUp(self):
        """
        Set up the test by creating a valid Xero token in the database, and
        defining the URL of the UpdateChartOfAccountsAPIView.
        """
        self.token = XeroToken.objects.create(
            access_token="valid_access_token",
            refresh_token="valid_refresh_token",
            expires_in=3600,
        )
        self.url = "/api/v1/xero/accounts/update/"

    @patch("requests.get")
    def test_successful_account_update(self, mock_get):
        """
        Test that the API successfully updates the Chart of Accounts and returns the correct data.

        On success, the API should return a 200 status code and the updated Chart of Accounts.
        The test also checks that the Chart of Accounts has been saved to the database.
        """
        mock_response = {
            "Accounts": [
                {
                    "AccountID": "f33b5b6d-8c40-4502-94b1-bb9acbed4589",
                    "Code": "A001",
                    "Name": "Cash Account",
                    "Type": "Asset",
                    "BankAccountNumber": "123456",
                    "Status": "ACTIVE",
                    "Description": "Main cash account",
                    "BankAccountType": "Bank",
                    "CurrencyCode": "USD",
                    "TaxType": "GST",
                    "EnablePaymentsToAccount": True,
                    "ShowInExpenseClaims": True,
                    "Class": "Class A",
                    "SystemAccount": "System A",
                    "ReportingCode": "RC001",
                    "ReportingCodeName": "Reporting 1",
                    "HasAttachments": False,
                    "UpdatedDateUTC": "2025-01-01T00:00:00Z",
                    "AddToWatchlist": False,
                }
            ]
        }
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Chart of Accounts retrieved successfully")
        self.assertEqual(len(response.data["data"]), 1)
        self.assertEqual(response.data["data"][0]["name"], "Cash Account")
        self.assertEqual(response.data["data"][0]["code"], "A001")

        account = ChartOfAccount.objects.get(account_id="f33b5b6d-8c40-4502-94b1-bb9acbed4589")
        self.assertEqual(account.name, "Cash Account")
        self.assertEqual(account.code, "A001")

    @patch("requests.get")
    def test_no_token_found(self, mock_get):
        """
        Test that the API returns a 400 status code and an appropriate error message
        when there is no Xero token present in the database.
        """
        XeroToken.objects.all().delete()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "No token found")

    @patch("requests.get")
    def test_token_expired(self, mock_get):
        """
        Test that the API returns a 401 status code and an appropriate error message
        when the Xero token is expired.
        """
        mock_get.return_value.status_code = 401
        mock_get.return_value.json.return_value = {"error": "Unauthorized - Token expired"}

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["error"], "Unauthorized - Token expired")

    @patch("requests.get")
    def test_empty_account_list(self, mock_get):
        """
        Test that the API returns a 200 status code and an empty list when
        Xero returns an empty list of Chart of Accounts.
        """
        mock_response = {"Accounts": []}
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Chart of Accounts retrieved successfully")
        self.assertEqual(len(response.data["data"]), 0)

    @patch("requests.get")
    def test_create_new_account_on_update(self, mock_get):
        """
        Test that the API creates a new Chart of Account object when the API is called
        and Xero returns a new Chart of Account that does not exist in the database.

        This test case also verifies that the API returns a 200 status code and a
        list of Chart of Accounts containing the newly created account.
        """
        mock_response = {
            "Accounts": [
                {
                    "AccountID": "f33b5b6d-8c40-4502-94b1-bb9acbed4589",
                    "Code": "A002",
                    "Name": "New Account",
                    "Type": "Liability",
                    "BankAccountNumber": "654321",
                    "Status": "ACTIVE",
                    "Description": "New account description",
                    "BankAccountType": "Bank",
                    "CurrencyCode": "USD",
                    "TaxType": "GST",
                    "EnablePaymentsToAccount": True,
                    "ShowInExpenseClaims": False,
                    "Class": "Class B",
                    "SystemAccount": "System B",
                    "ReportingCode": "RC002",
                    "ReportingCodeName": "Reporting 2",
                    "HasAttachments": True,
                    "UpdatedDateUTC": "2025-01-01T00:00:00Z",
                    "AddToWatchlist": True,
                }
            ]
        }
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Chart of Accounts retrieved successfully")
        self.assertEqual(len(response.data["data"]), 1)

        account = ChartOfAccount.objects.get(account_id="f33b5b6d-8c40-4502-94b1-bb9acbed4589")
        self.assertEqual(account.name, "New Account")
        self.assertEqual(account.code, "A002")

class ChartOfAccountsAllAPIViewTests(APITestCase):
    def setUp(self):
        """
        Create a Chart of Account for test data. This is needed because the API
        requires a Chart of Account to exist in order to retrieve it.
        """
        ChartOfAccount.objects.create(
            account_id="ca8ebab9-93ee-4ac1-b81a-cd52ac995f64",
            code="A001",
            name="Cash Account",
            type="Asset",
            status="Active",
            currency_code="USD"
        )

    def test_get(self):
        """
        Test that the API returns a 200 status code when accessing the endpoint.
        """
        response = self.client.get("/api/v1/xero/accounts/all/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_empty(self):
        """
        Test that the API returns an empty list when there are no Chart of Accounts.
        """
        ChartOfAccount.objects.all().delete()
        response = self.client.get("/api/v1/xero/accounts/all/")
        self.assertEqual(len(response.data["results"]), 0)
    
    def test_non_empty(self):
        """
        Test that the API returns the correct data when there are Chart of Accounts.
        """
        response = self.client.get("/api/v1/xero/accounts/all/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        accounts = ChartOfAccount.objects.all()
        expected_data = ChartOfAccountSerializer(accounts, many=True).data
        self.assertEqual(response.data["results"], expected_data)

    def test_pagination(self):
        """
        Test that the API supports pagination when there are more than 10 accounts.
        """
        for i in range(4, 25):
            ChartOfAccount.objects.create(
                account_id=uuid.uuid4(),
                code=f"A001{i}",
                name=f"Cash Account {i}",
                type="Asset",
                status="Active",
                currency_code="USD"
            )
        
        response = self.client.get("/api/v1/xero/accounts/all/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)
        self.assertGreater(len(response.data["results"]), 0)
        self.assertLessEqual(len(response.data["results"]), 10)
