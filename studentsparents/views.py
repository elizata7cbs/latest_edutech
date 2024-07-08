from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from studentsparents.models import StudentsParents
from studentsparents.serializers import StudentsParentsSerializers
from utils.ApiResponse import ApiResponse

class StudentsParentsView(viewsets.ModelViewSet):
    queryset = StudentsParents.objects.all()
    serializer_class = StudentsParentsSerializers

    @action(detail=False, methods=['get'], url_path='students-by-parent/(?P<parent_idno>[^/.]+)')
    def students_by_parent(self, request, parent_idno=None):
        studentsparents_records = StudentsParents.objects.filter(parentID__parentIdno=parent_idno).select_related('studentID', 'parentID')

        if studentsparents_records.exists():
            students_data = []
            for record in studentsparents_records:
                student = record.studentID

                student_data = {
                    'firstName': student.firstName,
                    'lastName': student.lastName,
                    'balance': record.get_balance(),  # Fetch balance dynamically
                }
                students_data.append(student_data)

            response = {
                "message": "Records retrieved",
                "status_code": 200,
                "data": students_data
            }
        else:
            response = {
                "message": "No records found for the provided parent ID number",
                "status_code": 404,
                "data": []
            }

        return Response(response, status=status.HTTP_200_OK if studentsparents_records.exists() else status.HTTP_404_NOT_FOUND)
