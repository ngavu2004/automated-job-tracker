import os
import base64
import re
import email
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from googleapiclient.errors import HttpError
from .parsers import OpenAIExtractor
from .authenticate import get_gmail_service, get_googlesheet_service
from .googlesheet_services import add_job_to_sheet, get_first_sheet_name
from .models import JobApplied, FetchLog
from google.auth.exceptions import RefreshError

openai_extractor = OpenAIExtractor()
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
    
def extract_body(mime_msg):
    content = []
    try:
        if mime_msg.is_multipart():
            for part in mime_msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    charset = part.get_content_charset() or "utf-8"
                    content.append(part.get_payload(decode=True).decode(charset, errors="replace"))
                elif content_type == "text/html" and "attachment" not in content_disposition:
                    charset = part.get_content_charset() or "utf-8"
                    html = part.get_payload(decode=True).decode(charset, errors="replace")
                    soup = BeautifulSoup(html, "html.parser")
                    content.append(soup.get_text())
        else:
            content_type = mime_msg.get_content_type()
            if content_type == "text/plain":
                charset = mime_msg.get_content_charset() or "utf-8"
                content.append(mime_msg.get_payload(decode=True).decode(charset, errors="replace"))
            elif content_type == "text/html":
                charset = mime_msg.get_content_charset() or "utf-8"
                html = mime_msg.get_payload(decode=True).decode(charset, errors="replace")
                soup = BeautifulSoup(html, "html.parser")
                content.append(soup.get_text())
    except Exception as e:
        print(f"Error extracting body: {e}")
    return "\n".join(content).replace('\n', '').replace('\r', '').strip()

def get_user_job_count(user):
    return JobApplied.objects.filter(user=user).count()

def get_emails(user):
    try:
        print("User is authorized:", is_user_authorized(user))
        gmail_service = get_gmail_service(user)
        print("Gmail service obtained.")
        sheet_service = get_googlesheet_service(user)
        print("Google Sheets service obtained.")
        first_sheet_name = get_first_sheet_name(sheet_service, user.google_sheet_id)
        user_job_count = get_user_job_count(user)
        print(f"User job count: {user_job_count}")
        curr_job_count = user_job_count + 1

        fetch_log = FetchLog.objects.filter(user=user).order_by('-last_fetch_date').first()
        if fetch_log and fetch_log.last_fetch_date:
            last_fetch_date = fetch_log.last_fetch_date
        else:
            # return error if no fetch log exists
            print("No fetch log found for the user.")
            return

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
        batch_size = int(os.getenv("FETCH_BATCH_SIZE", 10))  # Adjust as needed

        while True:
            results = gmail_service.users().messages().list(
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
                msg_data = gmail_service.users().messages().get(userId='me', id=msg["id"], format='raw').execute()
                if 'raw' not in msg_data:
                    print(f"Message {msg['id']} does not have raw content, skipping.")
                    continue
                mime_msg = email.message_from_bytes(base64.urlsafe_b64decode(msg_data['raw']))
                sender = mime_msg['from']
                subject = mime_msg['subject'] if mime_msg['subject'] else "No Subject"

                # Extract email body
                body = extract_body(mime_msg)

                # Extract job application data
                is_job_application_email, job_title, company_name, application_status = extract_email_data(subject, body)

                if is_job_application_email:
                    job_applied, created = JobApplied.objects.get_or_create(
                        user=user,
                        job_title=job_title,
                        company=company_name,
                        defaults={'status': application_status, 'sender_email': sender, 'row_number': curr_job_count+1}
                    )
                    if created:
                        curr_job_count += 1
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
                add_job_to_sheet(sheet_service, first_sheet_name, job_list, user.google_sheet_id)
                print(f"Added {len(job_list)} jobs to the Google Sheet.")

            # Check for next page
            next_page_token = results.get("nextPageToken")
            if not next_page_token:
                break  # No more pages

        # Create fetch log with the current date
        FetchLog.objects.create(last_fetch_date=now, user=user)
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

def _dummy(subject, body):
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