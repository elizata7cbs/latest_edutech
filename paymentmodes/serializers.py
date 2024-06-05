from rest_framework import serializers

from paymentmodes.models import PaymentModes


class PaymentModesSerializers(serializers.ModelSerializer):

    class Meta:
        model = PaymentModes
        fields = "__all__"
