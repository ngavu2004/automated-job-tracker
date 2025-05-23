import os
import json
import pandas as pd
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Scopes for Gmail and Google Sheets
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly",
          "https://www.googleapis.com/auth/spreadsheets"]

# Your Google Sheet ID
SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")

# Create a directory for storing credentials if it doesn't exist
CREDENTIALS_PATH = "credentials.json"

if not os.path.exists(CREDENTIALS_PATH):
    credentials_dict = {
        "installed": {
            "client_id": os.environ.get("GOOGLE_API_CLIENT_ID"),
            "project_id": os.environ.get("GOOGLE_API_PROJECT_ID"),
            "auth_uri": os.environ.get("GOOGLE_API_AUTH_URI"),
            "token_uri": os.environ.get("GOOGLE_API_TOKEN_URI"),
            "auth_provider_x509_cert_url": os.environ.get("GOOGLE_API_AUTH_PROVIDER_X509_CERT_URL"),
            "client_secret": os.environ.get("GOOGLE_API_CLIENT_SECRET"),
            "redirect_uris": [os.environ.get("GOOGLE_API_REDIRECT_URI")],
        }
    }
    with open(CREDENTIALS_PATH, "w") as f:
        json.dump(credentials_dict, f)

def get_gmail_service():
    """Authenticate and return Gmail service clients."""
    creds = None
    print("Path: ", os.getcwd())
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    gmail_service = build("gmail", "v1", credentials=creds)
    return gmail_service

def get_googlesheet_service():
    """Authenticate and return Google Sheets service client."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    sheets_service = build("sheets", "v4", credentials=creds)
    return sheets_service