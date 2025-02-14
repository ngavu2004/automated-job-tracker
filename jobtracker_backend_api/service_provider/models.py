from django.db import models

# Create your models here.
class Email(models.Model):
    sender = models.EmailField()
    subject = models.CharField(max_length=255)
    body = models.TextField()
    received_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name 
    
class JobApplied(models.Model):
    job_title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)

    def __str__(self):
        return self.job_title