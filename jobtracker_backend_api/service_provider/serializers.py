from django.contrib.auth.models import Group, User
from .models import Email, JobApplied, FetchLog
from django.db import models
from rest_framework import serializers

class EmailSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Email
        fields = '__all__'
        indexes = [
            models.Index(fields=['sender', 'received_at']),
        ]

class JobAppliedSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = JobApplied
        fields = '__all__'
        indexes = [
            models.Index(fields=['job_title', 'company', 'email_sender']),
        ]

class FetchLogSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = FetchLog
        fields = '__all__'
        indexes = [
            models.Index(fields=['last_fetch_date']),
        ]