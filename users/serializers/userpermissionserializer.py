from django.contrib.auth.models import Permission
from rest_framework import serializers


class PermissionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission  # Replace with your user model
        fields = '__all__'
