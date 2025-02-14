import os
import base64
import re
import pandas as pd
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from .authenticate import get_gmail_service
from .models import Email

def get_emails():
    """Fetch unread recruiter emails from Gmail."""
    try:
        # Get Gmail service
        service = get_gmail_service()
        # Call the Gmail API
        results = service.users().messages().list(userId="me").execute()
        messages = results.get("messages", [])

        email_data = []
        for msg in messages:
            msg_data = service.users().messages().get(userId="me", id=msg["id"]).execute()
            payload = msg_data["payload"]
            headers = payload["headers"]

            subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
            sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown Sender")

            # Extract email body
            parts = payload.get("parts", [])
            body = ""
            for part in parts:
                if part["mimeType"] == "text/plain":
                    body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")

            # Check if the email already exists in the database
            if not Email.objects.filter(sender=sender, subject=subject, body=body).exists():
                Email.objects.create(sender=sender, subject=subject, body=body)
    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f"An error occurred: {error}")