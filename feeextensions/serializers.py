from rest_framework import serializers

from feeextensions.models import FeeExtensions


class FeeExtensionsSerializers(serializers.ModelSerializer):

    class Meta:
        model = FeeExtensions
        fields = "__all__"
