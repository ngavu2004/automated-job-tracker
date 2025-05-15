from django.db import models

# Create your models here.
class Email(models.Model):
    sender = models.EmailField()
    subject = models.CharField(max_length=255)
    body = models.TextField()
    received_at = models.DateTimeField()
    fetch_date = models.DateTimeField(null=True)
    def __str__(self):
        return self.name 
    
class JobApplied(models.Model):
    job_title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    sender_email = models.EmailField(null=True)
    row_number = models.IntegerField(null=True)
    def __str__(self):
        return self.job_title
    
class FetchLog(models.Model):
    last_fetch_date = models.DateTimeField()

    def __str__(self):
        return f"Last fetch date: {self.last_fetch_date}"