from rest_framework import serializers

from expensetypes.models import ExpenseTypes
from expensetypes.serializers import ExpenseTypesSerializer
from .models import Expenses, ExpensePayment


class ExpensesSerializer(serializers.ModelSerializer):
    expensetypes = ExpenseTypesSerializer()

    class Meta:
        model = Expenses
        fields = ['amount', 'expenseID', 'expensetypes']

    def create(self, validated_data):
        expensetypes_data = validated_data.pop('expensetypes')
        expensetype = ExpenseTypes.objects.create(**expensetypes_data)
        expense = Expenses.objects.create(expensetypes=expensetype, **validated_data)
        return expense


class ExpensePaymentSerializer(serializers.ModelSerializer):
    remaining_balance = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)

    class Meta:
        model = ExpensePayment
        fields = ['expense', 'debited_account', 'amount_paid', 'remaining_balance', 'reference_number']

    def create(self, validated_data):
        # Create the ExpensePayment instance
        return super().create(validated_data)
