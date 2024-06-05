from rest_framework import serializers

from fee.models import StudentFeeCategories, FeeCategoryTransaction


class StudentFeeCategoriesSerializers(serializers.ModelSerializer):
    class Meta:
        model = StudentFeeCategories
        fields = "__all__"


class FeeCategoryTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeCategoryTransaction
        fields = '__all__'
