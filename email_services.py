import os
import base64
import re
import pandas as pd
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def extract_job_title(subject, body):
    """Extract job title from subject or body."""
    match = re.search(r"(?:(Hiring|Opportunity): )?([A-Za-z ]+)", subject)
    return match.group(2) if match else "Unknown Position"

def extract_company(body):
    """Extract company name from the email body."""
    match = re.search(r"at ([A-Z][a-z]+(?: [A-Z][a-z]+)*)", body)
    return match.group(1) if match else "Unknown Company"

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

            job_title = extract_job_title(subject, body)
            company = extract_company(body)
            email_data.append((job_title, company))

            # Mark email as read (optional)
            service.users().messages().modify(userId="me", id=msg["id"], body={"removeLabelIds": ["UNREAD"]}).execute()
        return email_data
    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f"An error occurred: {error}")