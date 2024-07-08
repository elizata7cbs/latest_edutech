from rest_framework import serializers


class givePermissionsSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    permissions = serializers.ListField(
        child=serializers.IntegerField()
    )
