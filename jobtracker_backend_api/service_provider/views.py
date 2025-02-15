from django.contrib.auth.models import Group, User
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions, viewsets, status
from .models import Email, JobApplied, FetchLog
from .email_services import get_emails, clear_email_table, extract_email_data
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

        # Create a new Email object
        sender = request.data.get('sender', '')
        received_date = request.data.get('received_at', '')
        Email.objects.create(sender=sender, subject=subject, body=body, received_at=received_date)

        job_title, company_name, application_status = extract_email_data(subject, body)
        
        # Check if the email is a job application email
        if job_title and company_name and application_status:
            print(f"Job Title: {job_title}\nCompany: {company_name}\nStatus: {application_status}")
            # Check if a JobApplied object with the same job title and company already exists
            job_applied, created = JobApplied.objects.get_or_create(
                job_title=job_title,
                company=company_name,
                defaults={'status': application_status}
            )
            if not created:
                print("Job application already exists.")
                # Update the status if the object already exists
                job_applied.status = application_status
                job_applied.save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=['get'])
    def fetch_emails(self, request):
        """
        Custom action to fetch emails from external source.
        """
        get_emails()
        return Response({"status": "Emails fetched and updated."})
    
    @action(detail=False, methods=['get'])
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

class FetchLogViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows the last fetch date to be viewed or edited.
    """
    queryset = FetchLog.objects.all()
    serializer_class = FetchLogSerializer