import os
import json
import pandas as pd
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from .models import User

# Scopes for Gmail and Google Sheets
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly",
          "https://www.googleapis.com/auth/spreadsheets"]

# Your Google Sheet ID
SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")

def get_google_auth_credentials(request):
    # get user from db which match email
    user = request.user
    if not user:
        raise ValueError("User not found in the request.")

    print("User google access token:", user.google_access_token)
    
    creds = Credentials(
        token=user.google_access_token,
        refresh_token=user.google_refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ["GOOGLE_API_CLIENT_ID"],
        client_secret=os.environ["GOOGLE_API_CLIENT_SECRET"],
    )
    return creds

def get_gmail_service(request):
    """Authenticate and return Gmail service clients."""
    creds = get_google_auth_credentials(request)
    gmail_service = build("gmail", "v1", credentials=creds)
    return gmail_service

def get_googlesheet_service(request):
    """Authenticate and return Google Sheets service client."""
    creds = get_google_auth_credentials(request)
    sheets_service = build("sheets", "v4", credentials=creds)
    return sheets_service
