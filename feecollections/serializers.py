from rest_framework import serializers
from feecollections.models import FeeCollections, Transaction
from students.models import Students
from utils.Helpers import Helpers


class FeeCollectionsSerializers(serializers.ModelSerializer):
    payment_mode = serializers.ChoiceField(choices=FeeCollections.PAYMENT_MODE_CHOICES)

    class Meta:
        model = FeeCollections
        fields = ['id', 'studentId', 'feecategory', 'uniqueid', 'payment_reference', 'payment_date',
                  'school_code', 'outstandingbalance', 'grade', 'receipt_number', 'payment_mode', 'debit', 'credit']

    def create(self, validated_data):
        # Generate receipt number
        receipt_number = Helpers.generate_receipt_number()

        # Create FeeCollections instance with the generated receipt number
        fee_collection = FeeCollections.objects.create(receipt_number=receipt_number, **validated_data)
        return fee_collection


class TransactionSerializers(serializers.ModelSerializer):
    student_id = serializers.PrimaryKeyRelatedField(queryset=Students.objects.all(), source='studentId')

    class Meta:
        model = Transaction
        fields = ['description', 'debit', 'credit', 'outstandingbalance', 'student_id']

    def create(self, validated_data):
        # Compute outstanding balance
        outstanding_balance = validated_data.get('debit', 0) - validated_data.get('credit', 0)
        validated_data['outstandingbalance'] = outstanding_balance

        # Create Transaction instance
        transaction = Transaction.objects.create(**validated_data)
        return transaction
