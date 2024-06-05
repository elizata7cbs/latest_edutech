from django.contrib.auth.hashers import make_password
from django.db.models import Q, F
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, permissions
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.schemas import openapi
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

import usergroup
from schools.models import Schools
from usergroup.models import UserGroup
from users.models import CustomUser
from users.serializers import CustomUserSerializer
from utils.ApiResponse import ApiResponse


# Create your views here.


class CustomUserView(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    # authentication_classes = [JSONWebTokenAuthentication, SessionAuthentication, BasicAuthentication]
    # permisson_classes = [IsAuthenticated]i
    @permission_classes([IsAuthenticated])
    def list(self, request, *args, **kwargs):
        response = ApiResponse()
        data = CustomUser.objects.all()

        # List to hold modified objects
        modified_data = []

        for instance in data:
            user_permissions = instance.user_permissions.all()  # Accessing user_permissions through the instance
            roles = [permission.name for permission in user_permissions]

            id = instance.id
            date_joined = instance.date_joined
            last_login = instance.last_login
            is_superuser = instance.is_superuser
            is_staff = instance.is_staff
            is_active = instance.is_active
            username = instance.username
            password = instance.password
            email = instance.email
            schools = instance.schools  # Assuming "school_id" is the correct attribute name
            first_name = instance.first_name
            last_name = instance.last_name
            middle_name = instance.middle_name
            gender = instance.gender
            usergroup_id = instance.usergroup_id  # Assuming "usergroup_id" is the correct attribute name
            date_of_birth = instance.date_of_birth
            nationality = instance.nationality
            address = instance.address
            school_name = instance.schools.name
            usergroup = instance.usergroup.name

            # Assuming "roles" is a ManyToManyField

            # Create a new object with the desired keys and values
            modified_object = {
                "id": instance.id,
                "date_joined": date_joined,
                "last_login": last_login,
                "is_superuser": is_superuser,
                "is_staff": is_staff,
                "is_active": is_active,
                "username": username,
                "password": password,
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "middle_name": middle_name,
                "gender": gender,
                "usergroup": instance.usergroup.name,
                "date_of_birth": date_of_birth,
                "nationality": nationality,
                "address": address,
                "school_name": instance.schools.name,
                "roles": roles,  # Extract IDs of roles
            }

            modified_data.append(modified_object)

        response.setStatusCode(status.HTTP_200_OK)
        response.setMessage("Found")
        response.setEntity(modified_data)
        return Response(response.toDict(), status=response.status)

    @permission_classes([IsAuthenticated])
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
        customerData = CustomUserSerializer(data=request.data)
        print(customerData)

        if not customerData.is_valid():
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "Please fill in the details correctly.", "status": status_code}, status_code)

        # Check if the email is already in use
        email = request.data.get("email")
        fname = request.data.get("first_name")
        existing_customer = CustomUser.objects.filter(email=email).first()

        if existing_customer:
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "Email is already in use.", "status": status_code}, status_code)

        # If email is not in use, save the new customer
        customerData.save()
        response.setStatusCode(status.HTTP_201_CREATED)
        response.setMessage("Created")
        response.setEntity(request.data)
        return Response(response.toDict(), status=response.status)

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
