from django.contrib.auth.models import Group, User
from .models import Email, JobApplied, FetchLog
from rest_framework import serializers

class EmailSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Email
        fields = '__all__'

class JobAppliedSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = JobApplied
        fields = '__all__'

class FetchLogSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = FetchLog
        fields = '__all__'