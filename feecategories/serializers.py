from rest_framework import serializers

from feecategories.models import FeeCategories


class FeeCategoriesSerializers(serializers.ModelSerializer):
    class Meta:
        model = FeeCategories
        fields = ['name', 'grade', 'term', 'amount']
