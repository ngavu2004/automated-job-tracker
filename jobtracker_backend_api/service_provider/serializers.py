from django.contrib.auth.models import Group
from .models import User, JobApplied, FetchLog, GoogleSheet
from django.db import models
from rest_framework import serializers



class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
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

class GoogleSheetSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = GoogleSheet
        fields = '__all__'
        indexes = [
            models.Index(fields=['sheet_id']),
        ]