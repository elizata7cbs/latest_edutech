from rest_framework import serializers

from supplierspayment.models import SuppliersPayment


class SuppliersPaymentSerializers(serializers.ModelSerializer):

    class Meta:
        model = SuppliersPayment
        fields = "__all__"
