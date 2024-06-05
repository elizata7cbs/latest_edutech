from rest_framework import serializers

from feepayments.models import FeePayments


class FeePaymentsSerializers(serializers.ModelSerializer):

    class Meta:
        model = FeePayments
        fields = "__all__"


class FeePaymentsSerializers:
    pass