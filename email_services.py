import os
import base64
import re
import pandas as pd
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from parsing_services import get_company_name, get_job_title, extract_job_application

def get_recruiter_emails(service):
    """Fetch unread recruiter emails from Gmail."""
    try:
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

            print("-" * 50)
            email_data = extract_job_application(subject, body)
            print(f"\n\nEmail data: {email_data}\n\n")
            # email_data.append((job_title, company))

            # Mark email as read (optional)
            # service.users().messages().modify(userId="me", id=msg["id"], body={"removeLabelIds": ["UNREAD"]}).execute()
        return email_data
    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f"An error occurred: {error}")