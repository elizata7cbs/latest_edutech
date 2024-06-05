from rest_framework import serializers

from students.models import Students


class StudentsSerializers(serializers.ModelSerializer):

    class Meta:
        model = Students
        fields = ["admNumber","schoolCode","firstName","middleName","lastName","studentGender","dob","dateOfAdmission","healthStatus","grade","stream","schoolStatus","dormitory","parentIdno","schoolID"]




class StudentsParentsSerializers:
    pass
