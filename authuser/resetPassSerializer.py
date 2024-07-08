from rest_framework import serializers


class ResetPassSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
