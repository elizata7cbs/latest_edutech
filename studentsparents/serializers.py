from rest_framework import serializers

from studentsparents.models import StudentsParents


class StudentsParentsSerializers(serializers.ModelSerializer):

    class Meta:
        model = StudentsParents
        fields = "__all__"
