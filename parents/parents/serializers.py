from rest_framework import serializers

from parents.models import Parents


class ParentsSerializers(serializers.ModelSerializer):

    class Meta:
        model = Parents
        fields = ['username', 'password']

