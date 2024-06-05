from rest_framework import serializers
from schools.models import Schools, SchoolAdmin, Branch

class SchoolsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schools
        fields = '__all__'

class SchoolAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolAdmin
        fields = '__all__'

class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = '__all__'
