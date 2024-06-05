from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from usergroup.models import UserGroup
from usergroup.serializers import UserGroupSerializers
from utils.ApiResponse import ApiResponse


# Create your views here.


class UserGroupView(viewsets.ModelViewSet):
    queryset = UserGroup.objects.all()

    serializer_class = UserGroupSerializers

    # authentication_classes = [JSONWebTokenAuthentication, SessionAuthentication, BasicAuthentication]
    # permission_classes = [IsAuthenticated]
    # @ has_permission()
    def list(self, request, *args, **kwargs):
        response = ApiResponse()
        data = list(UserGroup.objects.all().values())
        response.setStatusCode(status.HTTP_200_OK)
        response.setMessage("Found")
        response.setEntity(data)
        return Response(response.toDict(), status=response.status)

    def create(self, request, *args, **kwargs):
        response = ApiResponse()
        UserGroupData = UserGroupSerializers(data=request.data)

        if not UserGroupData.is_valid():
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "Please fill in the details correctly.", "status": status_code}, status_code)

        # Check if the email is already in use
        checkID = request.data.get("groupID")
        existingusergroup = UserGroup.objects.filter(groupID=checkID).first()

        if existingusergroup:
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "UserGroup  already exists.", "status": status_code}, status_code)

        # If email is not in use, save the new customer
        UserGroupData.save()
        response.setStatusCode(status.HTTP_201_CREATED)
        response.setMessage("UserGroup created")
        response.setEntity(request.data)
        return Response(response.toDict(), status=response.status)

    def destroy(self, request, *args, **kwargs):

        usergroupData = UserGroup.objects.filter(id=kwargs['pk'])
        if usergroupData:
            usergroupData.delete()
            status_code = status.HTTP_200_OK
            return Response({"message": "UserGroup data deleted Successfully", "status": status_code})
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "UserGroup data not found", "status": status_code})

    def update(self, request, *args, **kwargs):
        usergroup_details = UserGroup.objects.get(id=kwargs['pk'])
        usergroup_serializer_data = UserGroupSerializers(
            usergroup_details, data=request.data, partial=True)
        if usergroup_serializer_data.is_valid():
            usergroup_serializer_data.save()
            status_code = status.HTTP_201_CREATED
            return Response({"message": "UserGroup data Updated Successfully", "status": status_code})
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "UserGroup data Not found", "status": status_code})


