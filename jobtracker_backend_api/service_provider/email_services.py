import os
import base64
import re
import pandas as pd
from datetime import datetime, timezone
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from .parsers import OpenAIExtractor
from .authenticate import get_gmail_service
from .googlesheet_services import add_job_to_sheet
from .models import JobApplied, FetchLog, GoogleSheet
from google.auth.exceptions import RefreshError


def is_user_authorized(request):
    try:
        service = get_gmail_service(request)
        # Try a simple API call, e.g., get the user's profile
        profile = service.users().getProfile(userId="me").execute()
        print("User is authorized. Email:", profile.get("emailAddress"))
        return True
    except (HttpError, RefreshError) as error:
        print("User is NOT authorized or token is invalid:", error)
        return False

def get_emails(request):
    """Fetch unread recruiter emails from Gmail."""
    try:
        print("User is authorized:", is_user_authorized(request))
        # Get Gmail service
        service = get_gmail_service(request)
        print("Gmail service obtained.")
        # Define the date after which to retrieve emails
        # Get the last fetch date with this user email from the database
        fetch_log = FetchLog.objects.filter(user_id=request.user.email).order_by('-last_fetch_date').first()
        if fetch_log and fetch_log.last_fetch_date:
            last_fetch_date = fetch_log.last_fetch_date
        else:
            # If no fetch log exists, set the last fetch date to a date far in the past
            last_fetch_date =  datetime(2024, 10, 1, tzinfo=timezone.utc)

         # Determine the date to fetch emails from
        now = datetime.now(timezone.utc)
        if last_fetch_date.date() == now.date():
            # If emails were already fetched today, fetch only today's emails
            after_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            # If emails were not fetched today, fetch all emails since the last fetch date
            after_date = last_fetch_date

        # Convert the after_date to RFC 3339 format
        after_date = after_date.strftime("%Y/%m/%d")
        print(f"Fetching emails after: {after_date}")

        # Call the Gmail API
        results = service.users().messages().list(userId="me", q=f"after:{after_date}").execute()
        messages = results.get("messages", [])

        email_data = []
        print(f"Number of emails fetched: {len(messages)}")
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

            # Extract job application data
            is_job_application_email, job_title, company_name, application_status = extract_email_data(subject, body)

            # Check if the email is a job application email
            if is_job_application_email:
                # Check if a JobApplied object with the same job title and company already exists
                job_applied, created = JobApplied.objects.get_or_create(
                    job_title=job_title,
                    company=company_name,
                    defaults={'status': application_status, 'sender_email': sender, 'row_number': len(JobApplied.objects.all()) + 1}
                )
                # Update the status if the object already exists
                job_applied.status = application_status
                job_applied.save()
                # Add the job to the Google Sheet
                google_sheet = GoogleSheet.objects.filter(user_id=request.user.email).first()
                add_job_to_sheet(request, job_title, company_name, application_status, job_applied.row_number, google_sheet.sheet_id)

                print(f"Job application saved: {job_title} at {company_name} with status {application_status}")
        
        # Create fetch log with the current date
        FetchLog.objects.create(last_fetch_date=now, user_id=request.user.email)
    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f"An error occurred: {error}")

def extract_email_data(subject, body):
    openai_extractor = OpenAIExtractor()
    response = openai_extractor.get_response(subject, body)
    job_title = response.get("job_title", None)
    company_name = response.get("company_name", None)
    application_status = response.get("status", None)
    is_job_application_email = response.get("is_job_application_email", False)
    return is_job_application_email, job_title, company_name, application_status

def extract_email_data_dummy(subject, body):
    """Extract job application data from email."""
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