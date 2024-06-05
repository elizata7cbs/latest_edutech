from rest_framework import serializers

from payfee.models import Payments, RecordTransaction


class PaymentsSerializers(serializers.ModelSerializer):
    class Meta:
        model = Payments
        fields = 'student',  'phone_number', 'amount_paid',


class RecordTransactionSerializers(serializers.ModelSerializer):
    class Meta:
        model = RecordTransaction
        fields = 'description', 'debit', 'credit', 'balance', 'student_id',
