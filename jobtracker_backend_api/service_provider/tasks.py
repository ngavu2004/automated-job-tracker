from celery import shared_task
from django.contrib.auth import get_user_model
from .email_services import get_emails

@shared_task
def fetch_emails_task(user_id):
    User = get_user_model()
    user = User.objects.get(id=user_id)
    get_emails(user)