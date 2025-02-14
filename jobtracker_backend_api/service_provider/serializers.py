from django.contrib.auth.models import Group, User
from .models import Email
from rest_framework import serializers

class EmailSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Email
        fields = '__all__'