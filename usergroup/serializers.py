from django.contrib.auth.models import Group
from rest_framework import serializers


class UserGroupSerializers(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'
