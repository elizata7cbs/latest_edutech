from rest_framework import serializers

from inquiries.models import Inquiries


class InquiriesSerializers(serializers.ModelSerializer):

    class Meta:
        model = Inquiries
        fields = "__all__"
