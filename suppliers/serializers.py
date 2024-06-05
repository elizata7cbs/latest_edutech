from rest_framework import serializers

from suppliers.models import Suppliers


class SuppliersSerializers(serializers.ModelSerializer):
    class Meta:
        model = Suppliers
        fields = (
            'businessName', 'supplieridNO', 'prefix', 'firstname', 'middlename', 'lastname', 'phoneNumber', 'altPhone',
            'email', 'address', 'city', 'postalCode', 'country', 'openingBalance', 'dateCreated',)
