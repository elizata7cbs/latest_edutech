from rest_framework import serializers
from account.models import Account
from expensepayment.models import ExpensePayment
from expenses.models import Expenses


class ExpensePaymentSerializer(serializers.Serializer):
    PAYMENT_DESTINATION_CHOICES = (
        ('Bank', 'Bank'),
        ('M-Pesa', 'M-Pesa'),
    )

    payment_destination = serializers.ChoiceField(choices=PAYMENT_DESTINATION_CHOICES)
    payment_details = serializers.CharField(max_length=255, allow_blank=True, required=False)
    amount_paid = serializers.DecimalField(max_digits=15, decimal_places=2)
    expense = serializers.PrimaryKeyRelatedField(queryset=Expenses.objects.all())
    debited_account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all())
    source_account = serializers.CharField(max_length=20, allow_blank=True, required=False)
    destination_account = serializers.CharField(max_length=20, allow_blank=True, required=False)

    def validate(self, data):
        payment_destination = data.get('payment_destination')
        if payment_destination == 'Bank':
            if not data.get('source_account') or not data.get('destination_account'):
                raise serializers.ValidationError("Bank payments require source_account and destination_account.")
        elif payment_destination == 'M-Pesa':
            if not data.get('source_account') or not data.get('destination_account'):
                raise serializers.ValidationError("M-Pesa payments require phone_number and account_number.")
        return data

    def create(self, validated_data):
        payment_data = {
            'expense': validated_data.get('expense'),
            'debited_account': validated_data.get('debited_account'),
            'payment_details': validated_data.get('payment_details', ''),
            'amount_paid': validated_data.get('amount_paid')
        }
        payment = ExpensePayment.objects.create(**payment_data)
        return payment
