from rest_framework import serializers

from paymentgroups.models import PaymentGroups


class PaymentGroupsSerializers(serializers.ModelSerializer):

    class Meta:
        model = PaymentGroups
        fields = "__all__"
