from rest_framework import serializers

from schools.models import Schools
from students.models import Students


class StudentsSerializers(serializers.ModelSerializer):


    class Meta:
        model = Students
        fields = ["admNumber","firstName","middleName","lastName","studentGender","dob","upiNumber","grade","stream","parentID"]



class StudentsParentsSerializers:
    pass
