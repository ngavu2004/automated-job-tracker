from django.contrib.auth.models import Group, User
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions, viewsets, status
from .models import Email, JobApplied, FetchLog
from .email_services import get_emails, clear_email_table, extract_email_data
from .googlesheet_services import add_job_to_sheet
from .serializers import EmailSerializer, JobAppliedSerializer, FetchLogSerializer


class EmailViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows emails to be viewed or edited.
    """
    queryset = Email.objects.all().order_by('-received_at')
    serializer_class = EmailSerializer

    def create(self, request, *args, **kwargs):
        """
        Create a new Email object and extract job application data.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Extract job application data
        subject = request.data.get('subject', '')
        body = request.data.get('body', '')
        
        # Unpack all four values from extract_email_data
        is_job_application_email, job_title, company_name, application_status = extract_email_data(subject, body)
        
        # Check if the email is a job application email
        if is_job_application_email:
            print(f"Job Title: {job_title}\nCompany: {company_name}\nStatus: {application_status}")
            # Only process if job_title and company_name are present (to avoid incomplete data)
            if job_title and company_name:
                job_applied, created = JobApplied.objects.get_or_create(
                    job_title=job_title,
                    company=company_name,
                    defaults={'status': application_status or 'Unknown'}
                )
                if not created:
                    print("Job application already exists.")
                    # Update the status if the object already exists
                    if application_status:  # Only update if status is not None
                        job_applied.status = application_status
                        job_applied.save()
            else:
                print("Incomplete job application data; skipping JobApplied creation.")

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=['get', 'post'])
    def fetch_emails(self, request):
        """
        Custom action to fetch emails from external source.
        """
        get_emails()
        return Response({"status": "Emails fetched and updated."})
    
    @action(detail=False, methods=['get', 'post'])
    def clear(self, request):
        """Custom action to clear the Email table."""
        clear_email_table()
        return Response({"status": "Email table cleared."})

class JobAppliedViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows job applications to be viewed or edited.
    """
    queryset = JobApplied.objects.all().order_by('-id')
    serializer_class = JobAppliedSerializer

    @action(detail=False, methods=['post', 'get'])
    def update_all_to_google_sheet(self, request):
        """
        Custom action to update all emails to Google Sheets.
        """
        # For all jobs in the database, add them to the Google Sheet
        jobs = JobApplied.objects.all()
        for job in jobs:
            # Assuming job.job_title, job.company, and job.status are the fields to be added
            add_job_to_sheet(job.job_title, job.company, job.status, job.row_number)
        return Response({"status": "All emails updated to Google Sheets."})

class FetchLogViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows the last fetch date to be viewed or edited.
    """
    queryset = FetchLog.objects.all().order_by('-last_fetch_date')
    serializer_class = FetchLogSerializer