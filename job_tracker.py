from authenticate import authenticate_google
from email_services import get_recruiter_emails
if __name__ == "__main__":
    gmail_service, sheets_service = authenticate_google()
    get_recruiter_emails(gmail_service)
    