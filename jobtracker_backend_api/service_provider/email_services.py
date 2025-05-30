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


def is_user_authorized(user):
    try:
        service = get_gmail_service(user)
        # Try a simple API call, e.g., get the user's profile
        profile = service.users().getProfile(userId="me").execute()
        print("User is authorized. Email:", profile.get("emailAddress"))
        return True
    except (HttpError, RefreshError) as error:
        print("User is NOT authorized or token is invalid:", error)
        return False

def get_emails(user):
    try:
        print("User is authorized:", is_user_authorized(user))
        service = get_gmail_service(user)
        print("Gmail service obtained.")

        fetch_log = FetchLog.objects.filter(user=user).order_by('-last_fetch_date').first()
        if fetch_log and fetch_log.last_fetch_date:
            last_fetch_date = fetch_log.last_fetch_date
        else:
            last_fetch_date = datetime(2024, 10, 1, tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)
        if last_fetch_date.date() == now.date():
            after_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            after_date = last_fetch_date

        after_date = after_date.strftime("%Y/%m/%d")
        print(f"Fetching emails after: {after_date}")

        # Pagination setup
        next_page_token = None
        total_fetched = 0
        batch_size = 10  # Adjust as needed

        results = service.users().messages().list(
            userId="me",
            q=f"after:{after_date}",
            maxResults=batch_size,
            pageToken=next_page_token
        ).execute()
        messages = results.get("messages", [])
        print(f"Fetched {len(messages)} messages in this batch.")
        total_fetched += len(messages)

        job_list = []
        for msg in messages:
            msg_data = service.users().messages().get(userId="me", id=msg["id"]).execute()
            payload = msg_data["payload"]
            headers = payload["headers"]

            subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
            sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown Sender")
            received_timestamp = int(msg_data["internalDate"]) / 1000
            received_date = datetime.fromtimestamp(received_timestamp, tz=timezone.utc)

            # Extract email body
            parts = payload.get("parts", [])
            body = ""
            for part in parts:
                if part["mimeType"] == "text/plain":
                    body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")

            # Extract job application data
            is_job_application_email, job_title, company_name, application_status = extract_email_data(subject, body)

            if is_job_application_email:
                job_applied, created = JobApplied.objects.get_or_create(
                    job_title=job_title,
                    company=company_name,
                    defaults={'status': application_status, 'sender_email': sender, 'row_number': len(JobApplied.objects.all()) + 1}
                )
                job_applied.status = application_status
                job_applied.save()
                job_list.append({
                    "job_title": job_title,
                    "company": company_name,
                    "status": application_status,
                    "row_number": job_applied.row_number
                })

        # Add jobs to the Google Sheet for this batch
        if job_list:
            add_job_to_sheet(user, job_list, user.google_sheet_id)
            print(f"Added {len(job_list)} jobs to the Google Sheet.")

        # Check for next page
        next_page_token = results.get("nextPageToken")

        # Create fetch log with the current date
        FetchLog.objects.create(last_fetch_date=now, user=user)
        print(f"Total emails fetched: {total_fetched}")

    except HttpError as error:
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