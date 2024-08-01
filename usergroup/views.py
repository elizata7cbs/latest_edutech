from django.contrib.auth.models import Group, Permission
from rest_framework import viewsets, status
from rest_framework.response import Response

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
    # @allowed_users(allowed_roles=["admin"])
    def list(self, request, *args, **kwargs):
        response = ApiResponse()
        groups = Group.objects.all()
        data = []

        for group in groups:
            group_permissions = group.permissions.all()
            permissions = [
                {"id": perm.id, "name": perm.name, "codename": perm.codename}
                for perm in group_permissions
            ]
            group_data = {
                "id": group.id,
                "name": group.name,
                "permissions": permissions
            }
            data.append(group_data)

        response.setStatusCode(status.HTTP_200_OK)
        response.setMessage("Found")
        response.setEntity(data)
        return Response(response.toDict(), status=response.status)

    # @allowed_users(allowed_roles=["admin"])

    def create(self, request, *args, **kwargs):
        UserGroupData = self.get_serializer(data=request.data)

        if not UserGroupData.is_valid():
            status_code = status.HTTP_400_BAD_REQUEST
            return Response(
                {"message": "Please fill in the details correctly or Group already exists.", "status": status_code},
                status=status_code)

        name = request.data.get("name")
        existingusergroup = Group.objects.filter(name=name).first()

        if existingusergroup:
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "Group already exists.", "status": status_code}, status=status_code)

        group = UserGroupData.save()
        permission_codenames = [""]
        permissions = Permission.objects.filter(codename__in=permission_codenames)

        group.permissions.add(*permissions)

        return Response(
            {"message": "Group created", "status": status.HTTP_201_CREATED, "data": UserGroupData.data},
            status=status.HTTP_201_CREATED)
