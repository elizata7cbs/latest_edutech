from rest_framework import serializers

from academics.models import AcademicYear



class AcademicYearSerializers(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = ['academic_year_name',   'start_date', 'end_date', ]
