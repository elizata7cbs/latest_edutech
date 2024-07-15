from rest_framework import serializers

from allfees.models import FeeCollectionsAll


class FeeViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeCollectionsAll
        fields = '__all__'