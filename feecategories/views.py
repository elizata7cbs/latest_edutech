import os
import django
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import JsonResponse

from fee.models import StudentFeeCategories
from feecategories import models
from feecategories.models import FeeCategories, VirtualAccount
from students.models import Students

# Manually configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edutech_payment_engine.settings')
django.setup()
# from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.pagination import PageNumberPagination
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from feecategories.serializers import FeeCategoriesSerializers
from utils.ApiResponse import ApiResponse
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from utils.Helpers import Helpers


class FeeCategoriesView(viewsets.ModelViewSet):
    queryset = FeeCategories.objects.all()

    serializer_class = FeeCategoriesSerializers
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description', 'status']
    pagination_class = PageNumberPagination

    # authentication_classes = [JSONWebTokenAuthentication, SessionAuthentication]
    # permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        response = ApiResponse()
        data = list(FeeCategories.objects.all().values())
        response.setStatusCode(status.HTTP_200_OK)
        response.setMessage("Found")
        response.setEntity(data)
        return Response(response.toDict(), status=response.status)

    def list_virtual_account(self, request, *args, **kwargs):
        response = ApiResponse()
        helper = Helpers()
        virtual_accounts = VirtualAccount.objects.all()
        virtual_account_data = []
        for virtual_account in virtual_accounts:
            # Fetching the name from FeeCategories associated with VirtualAccount
            fee_category_name = virtual_account.category.name

            virtual_account_info = {
                'id': virtual_account.id,
                'account name': fee_category_name,
                'debit': virtual_account.debit,
                'credit': virtual_account.credit,
                'balance': virtual_account.balance,

            }
            virtual_account_data.append(virtual_account_info)

        response.setStatusCode(status.HTTP_200_OK)
        response.setMessage("Found")
        response.setEntity(virtual_account_data)
        return Response(response.toDict(), status=response.status)

    # def create(self, request, *args, **kwargs):
    #     response = ApiResponse()
    #     FeeCategoriesData = FeeCategoriesSerializers(data=request.data)
    #
    #     if not FeeCategoriesData.is_valid():
    #         status_code = status.HTTP_400_BAD_REQUEST
    #         return Response({"message": "Please fill in the details correctly.", "status": status_code}, status_code)
    #
    #     # If email is not in use, save the new customer
    #     FeeCategoriesData.save()
    #     response.setStatusCode(status.HTTP_201_CREATED)
    #     response.setMessage("FeeCategory created")
    #     response.setEntity(request.data)
    #     return Response(response.toDict(), status=response.status)

    def destroy(self, request, *args, **kwargs):

        regionData = FeeCategories.objects.filter(id=kwargs['pk'])
        if regionData:
            regionData.delete()
            status_code = status.HTTP_200_OK
            return Response({"message": "Users deleted Successfully", "status": status_code})
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "Users data not found", "status": status_code})

    def update(self, request, *args, **kwargs):
        users_details = FeeCategories.objects.get(id=kwargs['pk'])
        users_serializer_data = FeeCategoriesSerializers(
            users_details, data=request.data, partial=True)
        if users_serializer_data.is_valid():
            users_serializer_data.save()
            status_code = status.HTTP_201_CREATED
            return Response({"message": "Users Update Successfully", "status": status_code})
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "Users data Not found", "status": status_code})

    def deactivate(self, request, *args, **kwargs):
        # Deactivate a fee category
        instance = self.get_object()
        instance.status = 0
        instance.save()
        return Response({"message": "Fee category deactivated successfully"}, status=status.HTTP_200_OK)

    def filter_queryset(self, queryset):
        params = self.request.query_params
        filters = {}

        # Filter by name
        name_param = params.get('name')
        if name_param:
            filters['name__icontains'] = name_param

        # Filter by datePosted
        date_param = params.get('dateCreated')
        if date_param:
            filters['datePosted'] = date_param

        # Filter by status
        status_param = params.get('status')
        if status_param is not None:
            filters['status'] = status_param

        return queryset.filter(**filters)

    def createfeecategories(self, request):
        helper = Helpers()
        response = ApiResponse()
        print(request.data)

        name = request.data.get('name')
        description = request.data.get('description')
        categorycode = helper.generatecategorycode(name, description)
        apply_value = request.data.get('apply')
        # credit = float(request.data.get('credit'))
        # debit = float(request.data.get('debit'))

        fee_category = FeeCategories.objects.create(
            name=name,
            categorycode=categorycode,
            description=description,
            grade=request.data.get('grade'),
            term=request.data.get('term'),
            amount=request.data.get('amount'),
        )

        # Create virtual account
        # fee_category_instance = FeeCategories.objects.get(pk=None)
        # account = helper.create_virtual_account(fee_category_instance)
        # # balance = helper.calculate_balance(debit, credit)

        # # Check if the virtual account was created successfully
        # if virtual_account:
        #     message = "Virtual account created successfully."
        # else:
        #     message = "Failed to create virtual account."
        #
        # # Apply logic based on 'apply' value
        # if apply_value == 'all':
        #     # Add fee category to all students
        #     all_students = Students.objects.all()
        #     for student in all_students:
        #         student.fee_categories.add(fee_category)
        # elif apply_value == 'optional':
        #     # Do nothing for optional fee category
        #     pass
        # else:
        #     # Handle invalid 'apply' value
        #     return Response({'error': 'Invalid value for apply field'}, status=400)

        # Return the message
        return Response({ 'categorycode': categorycode})

    def calculate_total_fee(request, student_id):
        # Retrieve the student object
        student = Students.objects.get(pk=student_id)

        # Retrieve all fee categories associated with the student
        selected_categories = StudentFeeCategories.objects.filter(student=student)

        # Calculate the total fee
        total_fee = sum(category.amount for category in selected_categories)

        # Return the total fee as JSON response
        return JsonResponse({'total_fee': total_fee})