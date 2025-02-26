import os
import base64
import re
import pandas as pd
from datetime import datetime, timezone
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from .authenticate import get_gmail_service
from .models import Email, JobApplied

def get_emails():
    """Fetch unread recruiter emails from Gmail."""
    try:
        # Get Gmail service
        service = get_gmail_service()

        # Define the date after which to retrieve emails
        after_date = datetime(2025, 2, 1, tzinfo=timezone.utc)

        # Convert the after_date to RFC 3339 format
        after_date_rfc3339 = after_date.isoformat("T") + "Z"
        print(f"Fetching emails after: {after_date_rfc3339}")

        # Call the Gmail API
        results = service.users().messages().list(userId="me", q=f"after:{after_date_rfc3339}").execute()
        messages = results.get("messages", [])

        email_data = []
        for msg in messages:
            msg_data = service.users().messages().get(userId="me", id=msg["id"]).execute()
            payload = msg_data["payload"]
            headers = payload["headers"]

            subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
            sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown Sender")
            received_timestamp = int(msg_data["internalDate"]) / 1000  # Convert to seconds
            received_date = datetime.fromtimestamp(received_timestamp, tz=timezone.utc)

            # Extract email body
            parts = payload.get("parts", [])
            body = ""
            for part in parts:
                if part["mimeType"] == "text/plain":
                    body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")

            # Check if the email already exists in the database
            if not Email.objects.filter(sender=sender, subject=subject, body=body, received_at=received_date).exists():
                Email.objects.create(sender=sender, subject=subject, body=body, received_at=received_date)

            # Extract job application data
            job_title, company_name, application_status = extract_email_data(subject, body)

            # Check if the email is a job application email
            if job_title and company_name and application_status:
                # Check if a JobApplied object with the same job title and company already exists
                job_applied, created = JobApplied.objects.get_or_create(
                    job_title=job_title,
                    company=company_name,
                    defaults={'status': application_status}
                )
                if not created:
                    # Update the status if the object already exists
                    job_applied.status = application_status
                    job_applied.save()
    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f"An error occurred: {error}")

def clear_email_table():
    """Clear all records from the Email table."""
    Email.objects.all().delete()
    print("Email table cleared.")

def extract_email_data(subject, body):
    """Extract job application data from email."""
    # Example patterns to extract job title, company name, and application status
    job_title_patterns = [
        r"Job Title: (.+)",
        r"Position: (.+)",
        r"We are pleased to offer you the position of (.+)",
        r"You have been selected for the role of (.+)"
    ]

    company_name_patterns = [
        r"Company: (.+)",
        r"at (.+)",
        r"with (.+)"
    ]

    application_status_patterns = [
        r"Application Status: (.+)",
        r"Your application is (.+)",
        r"We are pleased to inform you that your application is (.+)"
    ]

    job_title = None
    company_name = None
    application_status = None

    # Check if the email is a job application email
    job_application_keywords = ["job", "position", "role", "application", "offer"]
    if not any(keyword in subject.lower() or keyword in body.lower() for keyword in job_application_keywords):
        return None, None, None

    for pattern in job_title_patterns:
        match = re.search(pattern, subject)
        if match:
            job_title = match.group(1)
            break

    if not job_title:
        for pattern in job_title_patterns:
            match = re.search(pattern, body)
            if match:
                job_title = match.group(1)
                break

    for pattern in company_name_patterns:
        match = re.search(pattern, subject)
        if match:
            company_name = match.group(1)
            break

    if not company_name:
        for pattern in company_name_patterns:
            match = re.search(pattern, body)
            if match:
                company_name = match.group(1)
                break

    for pattern in application_status_patterns:
        match = re.search(pattern, subject)
        if match:
            application_status = match.group(1)
            break

    if not application_status:
        for pattern in application_status_patterns:
            match = re.search(pattern, body)
            if match:
                application_status = match.group(1)
                break

    return job_title, company_name, application_status