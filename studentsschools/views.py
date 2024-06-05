# Create your views here.
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from studentsschools.models import StudentsSchools
from studentsschools.serializers import StudentsSchoolsSerializers
from utils.ApiResponse import ApiResponse


class StudentsSchoolsView(viewsets.ModelViewSet):
    queryset = StudentsSchools.objects.all()

    serializer_class = StudentsSchoolsSerializers

    # pagination_class = PageNumberPagination
    # authentication_classes = [JSONWebTokenAuthentication, SessionAuthentication, BasicAuthentication]
    # permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        response = ApiResponse()
        data = list(StudentsSchools.objects.all().values())
        response.setStatusCode(status.HTTP_200_OK)
        response.setMessage("Found")
        response.setEntity(data)
        return Response(response.toDict(), status=response.status)

    def create(self, request, *args, **kwargs):
        response = ApiResponse()
        StudentsSchoolsData = StudentsSchoolsSerializers(data=request.data)

        if not StudentsSchoolsData.is_valid():
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "Please fill in the details correctly.", "status": status_code}, status_code)

        # Check if the email is already in use
        checkschoolID = request.data.get("schoolID")
        existingschool = StudentsSchools.objects.filter(schoolID=checkschoolID).first()

        if existingschool:
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "StudentsSchools  already exists.", "status": status_code}, status_code)

        # If email is not in use, save the new customer
        StudentsSchoolsData.save()
        response.setStatusCode(status.HTTP_201_CREATED)
        response.setMessage("studentsschools found")
        response.setEntity(request.data)
        return Response(response.toDict(), status=response.status)

    def destroy(self, request, *args, **kwargs):

        studentsschoolData = StudentsSchools.objects.filter(id=kwargs['pk'])
        if studentsschoolData:
            studentsschoolData.delete()
            status_code = status.HTTP_200_OK
            return Response({"message": "StudentsSchools deleted Successfully", "status": status_code})
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "StudentsSchools data not found", "status": status_code})

    def updates(self, request, *args, **kwargs):
        studentchools_details = StudentsSchools.objects.get(id=kwargs['pk'])
        studentchools_serializer_data = StudentsSchoolsSerializers(
            studentchools_details, data=request.data, partial=True)
        if studentchools_serializer_data.is_valid():
            studentchools_serializer_data.save()
            status_code = status.HTTP_201_CREATED
            return Response({"message": "StudentsSchools Update Successfully", "status": status_code})
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "StudentsSchools data Not found", "status": status_code})
