import os

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


def _get_google_auth_credentials(google_access_token, google_refresh_token):
    """Get Google OAuth credentials for the user."""
    creds = Credentials(
        token=google_access_token,
        refresh_token=google_refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ["GOOGLE_API_CLIENT_ID"],
        client_secret=os.environ["GOOGLE_API_CLIENT_SECRET"],
    )
    return creds


def get_gmail_service(google_access_token, google_refresh_token):
    """Authenticate and return Gmail service clients."""
    creds = _get_google_auth_credentials(google_access_token, google_refresh_token)
    try:
        gmail_service = build("gmail", "v1", credentials=creds)
        return gmail_service
    except Exception as e:
        print(f"Error getting Gmail service: {e}")
        return None


def get_googlesheet_service(google_access_token, google_refresh_token):
    """Authenticate and return Google Sheets service client."""
    creds = _get_google_auth_credentials(google_access_token, google_refresh_token)
    sheets_service = build("sheets", "v4", credentials=creds)
    return sheets_service
