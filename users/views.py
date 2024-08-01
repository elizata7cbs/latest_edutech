from django.contrib.auth.models import Group, Permission
from django.db.models import Q, F
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import CustomUser
from users.permission_filter import allowed_users, allowed_groups
from users.serializers.LoginViewSerializer import LoginViewSerializer
from users.serializers.MyTokenObtainSerializer import MyTokenObtainPairSerializer
from users.serializers.givepermissionsserializer import givePermissionsSerializer
from users.serializers.serializers import CustomUserSerializer
from users.serializers.userpermissionserializer import PermissionsSerializer
from utils.ApiResponse import ApiResponse

from rest_framework_simplejwt.views import TokenObtainPairView


class CustomUserView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    @allowed_groups(allowed_groups=['superuser'])
    def list(self, request, *args, **kwargs):
        data = CustomUser.objects.all()
        modified_data = []
        for instance in data:
            roles = [group.name for group in instance.groups.all()]

            modified_object = {
                "id": instance.id,
                "date_joined": instance.date_joined,
                "last_login": instance.last_login,
                "is_superuser": instance.is_superuser,
                "is_staff": instance.is_staff,
                "is_active": instance.is_active,
                "username": instance.username,
                "email": instance.email,
                "first_name": instance.first_name,
                "last_name": instance.last_name,
                "middle_name": instance.middle_name,
                "gender": instance.gender,
                "date_of_birth": instance.date_of_birth,
                "nationality": instance.nationality,
                "address": instance.address,
                "school_name": instance.schools.name,
                "roles": roles,
            }
            modified_data.append(modified_object)
        return Response(modified_data, status=status.HTTP_200_OK)

    # @permission_classes([IsAuthenticated])
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        user_permissions = instance.user_permissions.all()  # Accessing user_permissions through the instance
        roles = [permission.name for permission in user_permissions]
        serializer = self.get_serializer(instance)
        data = serializer.data
        data['group'] = instance.usergroup.name
        data['school'] = instance.schools.name
        data['roles'] = roles
        return Response(data)

    def create(self, request, *args, **kwargs):
        response = ApiResponse()
        userData = CustomUserSerializer(data=request.data)

        if not userData.is_valid():
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "Please fill in the details correctly.", "status": status_code}, status_code)

        # Check if the email is already in use
        email = request.data.get("email")
        existing_user = CustomUser.objects.filter(email=email).first()

        if existing_user:
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "Email is already in use.", "status": status_code}, status_code)

        # If email is not in use, save the new customer
        user = userData.save()
        group = Group.objects.get(id=request.data.get('usergroup'))
        user.groups.add(group)

        response.setStatusCode(status.HTTP_201_CREATED)
        response.setMessage("Created")
        response.setEntity(userData.data)  # Use userData.data instead of request.data
        return Response(response.toDict(), status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        userData = CustomUser.objects.filter(id=kwargs['pk'])
        if userData:
            userData.delete()
            status_code = status.HTTP_200_OK
            return Response({"message": "CustomUser deleted Successfully", "status": status_code})
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "CustomUser data not found", "status": status_code})

    def update(self, request, *args, **kwargs):
        customuser_details = self.get_object()  # Get the object to be updated
        customuser_serializer_data = CustomUserSerializer(
            customuser_details, data=request.data, partial=True)  # Allow partial updates

        if customuser_serializer_data.is_valid():
            customuser_serializer_data.save()
            status_code = status.HTTP_200_OK  # Use HTTP_200_OK for successful update
            return Response({
                "message": "User's data updated successfully",
                "status": status_code,
                "data": customuser_serializer_data.data  # Return the updated data
            })
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({
                "message": "Validation failed",
                "status": status_code,
                "errors": customuser_serializer_data.errors  # Include validation errors in response
            })

    def filter_users(self, request, *args, **kwargs):
        columns = ['usergroup__name', 'username', 'email', 'id']  # Use '__' for traversing relationships
        search_param = kwargs.get('str', '')

        filters = Q()
        for column in columns:
            filters |= Q(**{f"{column}__icontains": search_param})

        # Applying filters to the queryset
        user_data = CustomUser.objects.filter(filters)

        if user_data.exists():
            # Fetch additional related data using annotations
            user_data = user_data.annotate(
                school_name=F('schools__name'),
                usergroup_name=F('usergroup__name')
            ).values('id', 'username', 'email', 'school_name', 'usergroup_name', 'date_joined', 'last_login',
                     'is_superuser', 'is_staff',
                     'is_active', 'password', 'first_name', 'last_name', 'gender', 'nationality', 'address',
                     'middle_name')

            response = {
                "message": "Records retrieved",
                "status_code": 200,
                "data": list(user_data)
            }
        else:
            response = {
                "message": "No records found for the provided search criteria",
                "status_code": 404,
                "data": []
            }

        return Response(response, status=status.HTTP_200_OK if user_data.exists() else status.HTTP_404_NOT_FOUND)

    def deactivate(self, request, *args, **kwargs):
        try:
            email = request.data.get('email')
            user = CustomUser.objects.get(email=email)
            serializer = CustomUserSerializer(instance=user, data={'is_active': False}, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "User deactivated successfully"}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except CustomUser.DoesNotExist:
            return Response({"message": "CustomUser not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": "An error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update_profile(self, request, *args, **kwargs):
        try:
            user_id = kwargs.get('pk')
            user = get_object_or_404(CustomUser, id=user_id)

            serializer = CustomUserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "User profile updated successfully.", "status": status.HTTP_200_OK})
            else:
                return Response({"message": "Invalid data provided.", "status": status.HTTP_400_BAD_REQUEST})

        except CustomUser.DoesNotExist:
            return Response({"message": "User not found.", "status": status.HTTP_404_NOT_FOUND})
        except Exception as e:
            return Response({"message": "An error occurred.", "status": status.HTTP_500_INTERNAL_SERVER_ERROR})


class PermissionsView(viewsets.ModelViewSet):
    serializer_class = PermissionsSerializer

    def list(self, request, *args, **kwargs):
        permissions = Permission.objects.all()
        p = []
        for perm in permissions:
            permissionData = {
                "name": perm.name,
                "content_type": perm.content_type.name,
                "codename": perm.codename,
                "id": perm.id

            }
            p.append(permissionData)
        response = ApiResponse()
        response.setStatusCode(status.HTTP_200_OK)
        response.setMessage("Found")
        response.setEntity(p)
        return Response(response.toDict(), status=response.status)

    def create(self, request, *args, **kwargs):
        response = ApiResponse()
        permissionsData = PermissionsSerializer(data=request.data)

        if not permissionsData.is_valid():
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "Please fill in the details correctly.", "status": status_code}, status_code)

        # Check if the name is already in use
        name = request.data.get("name")
        existing_permission = Permission.objects.filter(name=name).first()

        if existing_permission:
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "Name is already in use.", "status": status_code}, status_code)

        # If name is not in use, save the new permission
        permission = permissionsData.save()

        response.setStatusCode(status.HTTP_201_CREATED)
        response.setMessage("Created")
        response.setEntity(permissionsData.data)  # Use userData.data instead of request.data
        return Response(response.toDict(), status=status.HTTP_201_CREATED)

    def give_permissions(self, request):
        serializer = givePermissionsSerializer(data=request.data)
        if serializer.is_valid():
            group_name = serializer.validated_data.get('name')
            permission_ids = serializer.validated_data.get('permissions')

            try:
                group = Group.objects.get(name=group_name)
                permissions = Permission.objects.filter(id__in=permission_ids)
                group.permissions.add(*permissions)
                return Response({"message": "Permissions added successfully."}, status=status.HTTP_200_OK)
            except Group.DoesNotExist:
                return Response({"message": "Group not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendOTPView(APIView):
    serializer_class = LoginViewSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        return Response({'email': user.email}, status=status.HTTP_200_OK)


class LoginView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
