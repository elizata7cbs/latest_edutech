from rest_framework import serializers

from usergroup.models import UserGroup


class UserGroupSerializers(serializers.ModelSerializer):

    class Meta:
        model = UserGroup
        fields = "__all__"
