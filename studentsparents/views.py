# Create your views here.
from django.shortcuts import render
from rest_framework import viewsets, status
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

    # pagination_class = PageNumberPagination
    # authentication_classes = [JSONWebTokenAuthentication, SessionAuthentication, BasicAuthentication]
    # permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        response = ApiResponse()
        data = list(StudentsParents.objects.all().values())
        response.setStatusCode(status.HTTP_200_OK)
        response.setMessage("Found")
        response.setEntity(data)
        return Response(response.toDict(), status=response.status)

    def create(self, request, *args, **kwargs):
        response = ApiResponse()
        StudentsParentsData = StudentsParentsSerializers(data=request.data)

        if not StudentsParentsData.is_valid():
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "Please fill in the details correctly.", "status": status_code}, status_code)

        # Check if the email is already in use
        checkID = request.data.get("parentIdno")
        existingparent = StudentsParents.objects.filter(parentIdno=checkID).first()

        if existingparent:
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "StudentsParents  already exists.", "status": status_code}, status_code)

        # If email is not in use, save the new customer
        StudentsParentsData.save()
        response.setStatusCode(status.HTTP_201_CREATED)
        response.setMessage("Parent created")
        response.setEntity(request.data)
        return Response(response.toDict(), status=response.status)

    def destroy(self, request, *args, **kwargs):

        regionData = StudentsParents.objects.filter(id=kwargs['pk'])
        if regionData:
            regionData.delete()
            status_code = status.HTTP_200_OK
            return Response({"message": "Users deleted Successfully", "status": status_code})
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "Users data not found", "status": status_code})

    def update(self, request, *args, **kwargs):
        users_details = StudentsParents.objects.get(id=kwargs['pk'])
        users_serializer_data = StudentsParentsSerializers(
            users_details, data=request.data, partial=True)
        if users_serializer_data.is_valid():
            users_serializer_data.save()
            status_code = status.HTTP_201_CREATED
            return Response({"message": "Users Update Successfully", "status": status_code})
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "Users data Not found", "status": status_code})
