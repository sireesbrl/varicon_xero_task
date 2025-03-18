# Xero OAuth 2.0 Flow in Django

This project demonstrates how to implement Xero OAuth 2.0 authentication flow in a Django application.

## Features

- Login with Xero account
- Handle Xero OAuth callback
- Refresh access tokens
- Fetch Chart of Accounts from Xero

## Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/sireesbrl/varicon_xero_task.git
   cd varicon_xero_task
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Variables:**

   Create a `.env` file in the project root and add your Xero app credentials:

   ```
   XERO_CLIENT_ID=your_client_id
   XERO_CLIENT_SECRET=your_client_secret
   XERO_REDIRECT_URI=http://127.0.0.1:8000/api/v1/xero/callback/
   ```

4. **Run Migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Start the server:**
   ```bash
   python manage.py runserver
   ```

6. **Access the application:**
   Open your browser and go to `http://127.0.0.1:8000/api/v1/xero/login/` to start the Xero OAuth flow.

## Endpoints

- `/xero/login/`: Initiates the Xero OAuth login flow.
- `/xero/callback/`: Handles the OAuth callback from Xero.
- `/xero/refresh/`: Refreshes the Xero access token.
- `/xero/accounts/update/`: Updates the Chart of Accounts from Xero.
- `/xero/accounts/all/`: Displays the Chart of Accounts from Xero.

