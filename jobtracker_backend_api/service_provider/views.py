from django.contrib.auth.models import Group, User
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions, viewsets
from .models import Email
from .email_services import get_emails
from .serializers import EmailSerializer


class EmailViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows emails to be viewed or edited.
    """
    get_emails()
    queryset = Email.objects.all().order_by('-received_at')
    serializer_class = EmailSerializer