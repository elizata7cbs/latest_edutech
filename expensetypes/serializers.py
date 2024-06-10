
from rest_framework import serializers
from .models import ExpenseTypes


class ExpenseTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseTypes
        fields = ['name', 'description']
