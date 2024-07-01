from rest_framework import serializers
from .models import Expenses
from expensetypes.models import ExpenseTypes
from expensetypes.serializers import ExpenseTypesSerializer


class ExpensesSerializer(serializers.ModelSerializer):
    expensetypes = ExpenseTypesSerializer()

    class Meta:
        model = Expenses
        fields = ['amount', 'expensetypes', 'receipt']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be a positive number.")
        return value

    def validate_receipt(self, value):
        if value and not hasattr(value, 'file'):
            raise serializers.ValidationError("Receipt must be a valid file.")
        return value

    def create(self, validated_data):
        expensetypes_data = validated_data.pop('expensetypes')
        expensetype, created = ExpenseTypes.objects.get_or_create(**expensetypes_data)
        expense = Expenses.objects.create(expensetypes=expensetype, **validated_data)
        return expense

    def update(self, instance, validated_data):
        expensetypes_data = validated_data.pop('expensetypes', None)

        # Update or create expensetype if provided
        if expensetypes_data:
            expensetype, created = ExpenseTypes.objects.get_or_create(**expensetypes_data)
            instance.expensetypes = expensetype

        # Update the instance with the rest of the validated data
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
