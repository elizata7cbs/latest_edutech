
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from inquiries.models import Inquiries
from inquiries.serializers import InquiriesSerializers
from utils.ApiResponse import ApiResponse



class InquiriesView(viewsets.ModelViewSet):
    queryset = Inquiries.objects.all()

    serializer_class = InquiriesSerializers

    # pagination_class = PageNumberPagination
    # authentication_classes = [JSONWebTokenAuthentication, SessionAuthentication, BasicAuthentication]
    # permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        response = ApiResponse()
        data = list(Inquiries.objects.all().values())
        response.setStatusCode(status.HTTP_200_OK)
        response.setMessage("Found")
        response.setEntity(data)
        return Response(response.toDict(), status=response.status)

    def create(self, request, *args, **kwargs):
        response = ApiResponse()
        InquiriesData = InquiriesSerializers(data=request.data)

        if not InquiriesData.is_valid():
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "Please fill in the details correctly.", "status": status_code}, status_code)

        # Check if the email is already in use
        checkID = request.data.get("parentID")
        existinginquiry = Inquiries.objects.filter(parentID=checkID).first()

        if existinginquiry:
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "Inquiries  already exists.", "status": status_code}, status_code)

        # If email is not in use, save the new customer
        InquiriesData.save()
        response.setStatusCode(status.HTTP_201_CREATED)
        response.setMessage("Inquiry created")
        response.setEntity(request.data)
        return Response(response.toDict(), status=response.status)

    def destroy(self, request, *args, **kwargs):

        inquiriesData = Inquiries.objects.filter(id=kwargs['pk'])
        if inquiriesData:
            inquiriesData.delete()
            status_code = status.HTTP_200_OK
            return Response({"message": "Inquiries deleted Successfully", "status": status_code})
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "Inquiries data not found", "status": status_code})

    def update(self, request, *args, **kwargs):
        inquiries_details = Inquiries.objects.get(id=kwargs['pk'])
        inquiries_serializer_data = InquiriesSerializers(
            inquiries_details, data=request.data, partial=True)
        if inquiries_serializer_data.is_valid():
            inquiries_serializer_data.save()
            status_code = status.HTTP_201_CREATED
            return Response({"message": "Inquiries Update Successfully", "status": status_code})
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "Inquiries data Not found", "status": status_code})



