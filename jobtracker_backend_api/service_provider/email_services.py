import base64
import email
import os
from datetime import datetime, timezone

from bs4 import BeautifulSoup
from google.auth.exceptions import RefreshError
from googleapiclient.errors import HttpError

from .authenticate import get_gmail_service, get_googlesheet_service
from .googlesheet_services import add_job_to_sheet, get_first_sheet_name
from .models import FetchLog, JobApplied
from .parsers import OpenAIExtractor

openai_extractor = OpenAIExtractor()


def is_user_authorized(user):
    service = get_gmail_service(user.google_access_token, user.google_refresh_token)
    try:
        # Try a simple API call, e.g., get the user's profile
        service.users().getProfile(userId="me").execute()
        # print("User is authorized. Email:", profile.get("emailAddress"))
        return True
    except (HttpError, RefreshError) as error:
        print("User is NOT authorized or token is invalid:", error)
        return False

def extract_text_content(part):
    content_type = part.get_content_type()
    content_disposition = str(part.get("Content-Disposition"))
    if (
        content_type == "text/plain"
        and "attachment" not in content_disposition
    ):
        charset = part.get_content_charset() or "utf-8"
        
        return  part.get_payload(decode=True).decode(charset, errors="replace")
        
    elif (
        content_type == "text/html"
        and "attachment" not in content_disposition
    ):
        charset = part.get_content_charset() or "utf-8"
        html = part.get_payload(decode=True).decode(
            charset, errors="replace"
        )
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text()
    return None

def extract_body(mime_msg):
    single = not mime_msg.is_multipart()
    parts = [mime_msg] if single else list(mime_msg.walk())

    contents = []
    for part in parts:
        contents.append(extract_text_content(part))

    return "\n".join(contents).replace("\n", "").replace("\r", "").strip()


def get_user_job_count(user):
    return JobApplied.objects.filter(user=user).count()


def get_after_date(user):
    fetch_log = FetchLog.objects.filter(user=user).order_by("-last_fetch_date").first()
    last_fetch_date = fetch_log.last_fetch_date if fetch_log else None
    after_date = get_after_date(last_fetch_date, timezone.now())
    return after_date


def get_messages(gmail_service, after_date_string, next_page_token=None, batch_size=10):
    """Fetch messages from Gmail after a specific date."""
    try:
        results = (
            gmail_service.users()
            .messages()
            .list(
                userId="me",
                q=f"after:{after_date_string}",
                maxResults=batch_size,
                pageToken=next_page_token,
            )
            .execute()
        )
        return results.get("messages", []), results.get("nextPageToken")
    except HttpError as error:
        print(f"An error occurred while fetching messages: {error}")
        return [], None


def classify_email(gmail_service, user, msg, curr_job_count):
    msg_data = (
        gmail_service.users()
        .messages()
        .get(userId="me", id=msg["id"], format="raw")
        .execute()
    )
    if "raw" not in msg_data:
        print(f"Message {msg['id']} does not have raw content, skipping.")
        return None, None, None, None

    mime_msg = email.message_from_bytes(base64.urlsafe_b64decode(msg_data["raw"]))
    sender = mime_msg["from"]
    subject = mime_msg["subject"] if mime_msg["subject"] else "No Subject"

    # Extract email body
    body = extract_body(mime_msg)

    # Extract job application data
    (
        is_job_application_email,
        job_title,
        company_name,
        application_status,
    ) = extract_email_data(subject, body)

    if is_job_application_email:
        job_applied, created = JobApplied.objects.get_or_create(
            user=user,
            job_title=job_title,
            company=company_name,
            defaults={
                "status": application_status,
                "sender_email": sender,
                "row_number": curr_job_count + 1,
            },
        )
        if created:
            curr_job_count += 1
        job_applied.status = application_status
        job_applied.save()

    return job_title, company_name, application_status, job_applied


def get_emails(user):
    try:
        # print("User is authorized:", is_user_authorized(user))
        gmail_service = get_gmail_service(
            user.google_access_token, user.google_refresh_token
        )
        # print("Gmail service obtained.")
        sheet_service = get_googlesheet_service(
            user.google_access_token, user.google_refresh_token
        )
        # print("Google Sheets service obtained.")
        first_sheet_name = get_first_sheet_name(sheet_service, user.google_sheet_id)
        user_job_count = get_user_job_count(user)
        # print(f"User job count: {user_job_count}")
        curr_job_count = user_job_count + 1

        after_date = get_after_date(user)

        after_date_string = after_date.strftime("%Y/%m/%d")
        print(f"Fetching emails after: {after_date_string}")

        # Pagination setup
        next_page_token = None
        total_fetched = 0
        batch_size = int(os.getenv("FETCH_BATCH_SIZE", 10))  # Adjust as needed

        while True:
            messages, next_page_token = get_messages(
                gmail_service, after_date_string, next_page_token, batch_size
            )
            print(f"Fetched {len(messages)} messages in this batch.")
            total_fetched += len(messages)

            job_list = []
            for msg in messages:
                job_title, company_name, application_status, job_applied = (
                    classify_email(gmail_service, user, msg, curr_job_count)
                )
                if job_title:
                    job_list.append(
                        {
                            "job_title": job_title,
                            "company": company_name,
                            "status": application_status,
                            "row_number": job_applied.row_number,
                        }
                    )

            # Add jobs to the Google Sheet for this batch
            if job_list:
                add_job_to_sheet(
                    sheet_service, first_sheet_name, job_list, user.google_sheet_id
                )
                print(f"Added {len(job_list)} jobs to the Google Sheet.")

            # Check for next page
            if not next_page_token:
                break  # No more pages

        # Create fetch log with the current date
        FetchLog.objects.create(last_fetch_date=datetime.now(timezone.utc), user=user)
        print(f"Total emails fetched: {total_fetched}")

    except HttpError as error:
        print(f"An error occurred: {error}")


def extract_email_data(subject, body):
    response = openai_extractor.get_response(subject, body)
    job_title = response.get("job_title", None)
    company_name = response.get("company_name", None)
    application_status = response.get("status", None)
    is_job_application_email = response.get("is_job_application_email", False)
    return is_job_application_email, job_title, company_name, application_status
