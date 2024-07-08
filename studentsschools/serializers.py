from rest_framework import serializers

from studentsschools.models import StudentsSchools


class StudentsSchoolsSerializers(serializers.ModelSerializer):

    class Meta:
        model = StudentsSchools
        fields = "__all__"



