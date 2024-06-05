import os
from decimal import Decimal

import django
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from fee.models import StudentFeeCategories, FeeCategoryTransaction
from fee.serializers import StudentFeeCategoriesSerializers, FeeCategoryTransactionSerializer
from feecategories.models import VirtualAccount, FeeCategories

# Manually configure Django settings

# from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.pagination import PageNumberPagination
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from feecategories.serializers import FeeCategoriesSerializers
from payfee.models import RecordTransaction
from students.models import Students, StudentAccount
from utils.ApiResponse import ApiResponse
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from utils.Helpers import Helpers


class StudentFeeCategoriesView(viewsets.ModelViewSet):
    queryset = StudentFeeCategories.objects.all()

    serializer_class = StudentFeeCategoriesSerializers

    # authentication_classes = [JSONWebTokenAuthentication, SessionAuthentication]
    # permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        response = ApiResponse()
        fee = list(StudentFeeCategories.objects.all().values())
        response.setStatusCode(status.HTTP_200_OK)
        response.setMessage("Found")
        response.setEntity(fee)
        return Response(response.toDict(), status=response.status)

    # def select_fee(request):
    #     if request.method == 'POST':
    #         category_id = request.POST.get('category_id')
    #         amount_paid = request.POST.get('amount_paid')
    #         student = request.user.student  # Assuming the logged-in user is a student
    #         category = Fee.objects.get(id=category_id)
    #
    #         # Create the fee object
    #         fee = Fee.objects.create(student=student, category=category, amount_paid=amount_paid)
    #
    #         # Update the virtual account debit balance
    #         virtual_account, _ = VirtualAccount.objects.get_or_create(student=student)
    #         virtual_account.debit += float(amount)
    #         virtual_account.save()
    #
    #     categories = Fee.objects.all()
    #     return request, {'categories': categories}

    def select_fee(request):
        if request.method == 'POST':
            selected_category_ids = request.POST.getlist('selected_categories')
            student_id = request.user.id
            student = Students.objects.get(pk=student_id)
            selected_categories = FeeCategories.objects.filter(pk__in=selected_category_ids)

            total_amount = sum(category.amount for category in selected_categories)

            # Associate the selected fee categories with the student
            for category in selected_categories:
                StudentFeeCategories.objects.create(student=student, fee_category=category)

            # Call the helper method to update the student's account
            helper = Helpers()

            # Automatic debit student account when fee categories are added
            helper.debit_student_account(student, total_amount)

            # Automatic credit fee category account when fee categories are added to students
            helper.credit_fee_categories_virtual_account(selected_categories)

            # Automatic record debit when selected
            helper.record_debit_transaction(selected_categories)

            return JsonResponse({'message': 'Selected fee categories saved successfully'})
        else:
            return JsonResponse({'error': 'Invalid request method'}, status=400)

    def destroy(self, request, *args, **kwargs):

        regionData = StudentFeeCategories.objects.filter(id=kwargs['pk'])
        if regionData:
            regionData.delete()
            status_code = status.HTTP_200_OK
            return Response({"message": "Users deleted Successfully", "status": status_code})
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "Users data not found", "status": status_code})

    def update(self, request, *args, **kwargs):
        users_details = StudentFeeCategories.objects.get(id=kwargs['pk'])
        users_serializer_data = StudentFeeCategoriesSerializers(
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

    def get_total_fee_for_student(self, request, student_id):
        # Retrieve the student object or return a response if not found
        student = get_object_or_404(Students, pk=student_id)

        # Query StudentFeeCategory objects associated with the specified student
        student_fee_categories = StudentFeeCategories.objects.filter(student_id=student_id)

        # Initialize total fee amount
        total_fee = 0

        # Iterate over each StudentFeeCategory and sum up the amounts
        for student_fee_category in student_fee_categories:
            total_fee += student_fee_category.fee_category.amount

        # Return the total fee as a JSON response
        return Response({'total_fee': total_fee})

    def get_fee_structure(self, request, student_id):
        # Query StudentFeeCategory objects associated with the specified student
        student_fee_categories = StudentFeeCategories.objects.filter(student_id=student_id)

        # Initialize an empty list to store category details
        category_details = []

        # Iterate over each StudentFeeCategory
        for student_fee_category in student_fee_categories:
            # Retrieve the category details including the amount
            category_detail = {
                'category_id': student_fee_category.fee_category.id,
                'category_name': student_fee_category.fee_category.name,
                'amount': student_fee_category.fee_category.amount
            }
            # Append category detail to the list
            category_details.append(category_detail)

        # Return the list of category details as a JSON response
        return Response({'student_fee_categories': category_details})

    def get_payment_history(self, request, student_id):
        # Query all debit and credit records for the specified student
        transaction_records = StudentAccount.objects.filter(student_id=student_id)

        # Initialize a list to store the transaction record details
        transaction_details = []

        # Initialize balance
        balance = 0

        # Iterate over the transaction records
        for record in transaction_records:
            # Update balance
            balance += record.credit - record.debit

            # Append the transaction record details to the list
            transaction_details.append({
                'student': record.student,
                'debit': record.debit,
                'credit': record.credit,
                'balance': balance,
                'date': record.date
            })

        return Response({'payment_history': transaction_records})

    def get_transactions_for_student(self, request, student_id):
        """
        Retrieves all transactions for a specified student and calculates the balance for each transaction.

        Args:
            student_id (int): The ID of the student.

        Returns:
            Response: A JSON response containing all transactions for the specified student with calculated balances.
        """
        transactions = RecordTransaction.objects.filter(student_id=student_id).order_by('transaction_date').values()

        # Initialize balance
        balance = 0

        # Calculate balance for each transaction
        for transaction in transactions:
            balance += transaction['debit'] - transaction['credit']
            transaction['balance'] = balance

        return Response(transactions, status=status.HTTP_200_OK)

    def get_total_balance_for_student(self, request, student_id):
        """
        Retrieves the total balance for a specified student.

        Args:
            student_id (int): The ID of the student.

        Returns:
            Response: A JSON response containing the total balance for the specified student.
        """
        # Calculate the total debit and credit for the specified student
        total_debit = RecordTransaction.objects.filter(student_id=student_id).aggregate(Sum('debit'))['debit__sum'] or 0
        total_credit = RecordTransaction.objects.filter(student_id=student_id).aggregate(Sum('credit'))[
                           'credit__sum'] or 0

        # Calculate the total balance
        total_balance = total_debit - total_credit

        return Response({'student_id': student_id, 'total_balance': total_balance}, status=status.HTTP_200_OK)

    class ListFeeCategoryTransactionView(viewsets.ModelViewSet):
        queryset = FeeCategoryTransaction.objects.all()
        serializer_class = FeeCategoryTransactionSerializer
        filter_backends = [filters.SearchFilter]
        pagination_class = PageNumberPagination

    def list_category_records(self, request, *args, **kwargs):
        response = ApiResponse()  # Initialize your custom API response

        # Retrieve transactions with fee category information and order by transaction date
        data = FeeCategoryTransaction.objects.all().values(
            'id', 'student__uniqueId', 'feecategory__name', 'description', 'debit', 'credit',
            'balance', 'transaction_date', 'feecategory_id'
        ).order_by('transaction_date')  # Order by transaction date ascending

        # Initialize balance dictionary for each fee category
        category_balances = {}

        # Calculate and set balance for each transaction
        for transaction in data:
            category_id = transaction['feecategory_id']
            # Initialize balance for new fee category
            if category_id not in category_balances:
                category_balances[category_id] = 0

            # Calculate current balance
            current_balance = category_balances[category_id] + transaction['credit'] - transaction['debit']
            transaction['balance'] = current_balance

            # Update balance for the fee category
            category_balances[category_id] = current_balance

        response.setStatusCode(status.HTTP_200_OK)
        response.setMessage("FeeCategoryTransactions Found")
        response.setEntity(list(data))  # Convert to list to be JSON serializable
        return Response(response.toDict(), status=response.status)

    def percentage_of_each_category(self, request):
        # Calculate total debit across all transactions
        total_debit = FeeCategoryTransaction.objects.aggregate(total_debit=Sum('debit'))['total_debit'] or Decimal(
            '0.00')

        # Calculate percentage of debit for each fee category
        categories_with_percentage = []
        fee_categories = FeeCategories.objects.all()
        for category in fee_categories:
            category_debit = \
            FeeCategoryTransaction.objects.filter(feecategory=category).aggregate(total_debit=Sum('debit'))[
                'total_debit'] or Decimal('0.00')
            percentage = (category_debit / total_debit) * 100 if total_debit != 0 else Decimal('0.00')
            categories_with_percentage.append({'category': category.name, 'percentage': percentage})

        # Return the result as a JSON response
        return JsonResponse(categories_with_percentage, safe=False)
