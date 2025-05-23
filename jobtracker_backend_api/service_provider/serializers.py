from django.contrib.auth.models import Group, User
from .models import JobApplied, FetchLog
from django.db import models
from rest_framework import serializers



class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'email', 'access_token', 'refresh_token', 'token_expiry']
        indexes = [
            models.Index(fields=['email']),
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