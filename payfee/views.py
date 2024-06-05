import os
from decimal import Decimal
from operator import attrgetter

import django
from django.db.models import Sum

from expenses.models import Expenses
from fee.models import StudentFeeCategories
from feecategories.models import FeeCategories
from students.models import Students, StudentAccount
from suppliers.models import Suppliers

# Manually configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edutech_payment_engine.settings')
django.setup()
from utils.Helpers import Helpers
from payfee.models import Payments, RecordTransaction
from rest_framework.pagination import PageNumberPagination
from payfee.serializers import RecordTransactionSerializers, PaymentsSerializers
from utils.ApiResponse import ApiResponse
from datetime import date
from rest_framework import viewsets, status, filters
from rest_framework.response import Response


class PaymentView(viewsets.ModelViewSet):
    queryset = Payments.objects.all()
    serializer_class = PaymentsSerializers
    filter_backends = [filters.SearchFilter]
    pagination_class = PageNumberPagination

    # authentication_classes = [JSONWebTokenAuthentication, SessionAuthentication]
    # permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        response = ApiResponse()
        data = list(Payments.objects.all().values())
        response.setStatusCode(status.HTTP_200_OK)
        response.setMessage("Found")
        response.setEntity(data)
        return Response(response.toDict(), status=response.status)

    def destroy(self, request, *args, **kwargs):

        regionData = Payments.objects.filter(id=kwargs['pk'])
        if regionData:
            regionData.delete()
            status_code = status.HTTP_200_OK
            return Response({"message": "Users deleted Successfully", "status": status_code})
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "Users data not found", "status": status_code})

    def update(self, request, *args, **kwargs):
        fee_details = Payments.objects.get(id=kwargs['pk'])
        fee_serializer_data = PaymentsSerializers(
            fee_details, data=request.data, partial=True)
        if fee_serializer_data.is_valid():
            fee_serializer_data.save()
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

    def collect_fee(self, request):
        # Instantiate the Helpers class
        helper = Helpers()

        # Retrieve the data sent with the request
        unique_id = request.data.get('uniqueId')  # Use 'uniqueId' to reference the student
        amount_paid = request.data.get('amount_paid')
        payment_date = request.data.get('payment_date')
        # paymentmode = request.data.get('paymentmode')
        # reference = request.data.get('reference')
        phone_number = request.data.get('phone_number')

        # Check if phonenumber is provided and valid
        if not phone_number or not phone_number.isdigit():
            return Response(
                {'error': 'Phone number is missing or invalid.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Retrieve the student object using uniqueId
            student = Students.objects.get(uniqueId=unique_id)
        except Students.DoesNotExist:
            # Return a 404 response if the student is not found
            return Response(
                {'error': 'Student not found with the provided uniqueId.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Create a fee collection entry using uniqueId as the foreign key
        Payments.objects.create(
            student=student,
            amount_paid=amount_paid,
            # paymentmode=paymentmode,
            payment_date=payment_date,
            # reference=reference,
            phone_number=phone_number,
        )

        # Credit the student account and record the transaction
        helper.credit_student_account(student.uniqueId)  # Use uniqueId for crediting
        helper.record_credit_transaction(student.uniqueId)  # Use uniqueId for the record

        return Response({'amount_paid': amount_paid}, status=status.HTTP_201_CREATED)

    def calculate_total_fee(self, request):  # Add request parameter if needed
        fee_collections = Payments.objects.all()

        amount_paid = sum(float(fee.amount_paid) for fee in fee_collections)

        return Response({
            'Fee Collection': amount_paid,

        })

    def calculate_profit(self, request):
        # Calculate total expenses
        total_expenses = Expenses.objects.aggregate(total=Sum('amount_paid'))['total'] or Decimal('0.00')

        # Calculate total suppliers' opening balance
        total_suppliers = Suppliers.objects.aggregate(total=Sum('openingBalance'))['total'] or 0.0

        # Calculate total payments
        total_payments = Payments.objects.aggregate(total=Sum('amount_paid'))['total'] or Decimal('0.00')

        # Calculate profit
        profit = total_payments - (total_expenses + Decimal(total_suppliers))

        # Return the result as a JSON response
        data = {
            'total_expenses': float(total_expenses),
            'total_suppliers': float(total_suppliers),
            'total_payments': float(total_payments),
            'profit': float(profit)
        }
        return Response(data)

    class RecordTransactionView(viewsets.ModelViewSet):
        queryset = StudentAccount.objects.all()
        serializer_class = RecordTransactionSerializers
        filter_backends = [filters.SearchFilter]
        pagination_class = PageNumberPagination

    from django.utils import timezone

    def list_transaction(self, request, *args, **kwargs):
        response = ApiResponse()  # Initialize your custom API response

        # Retrieve transactions with student information and order by transaction date
        data = RecordTransaction.objects.all().values(
            'id', 'student__uniqueId', 'description', 'debit', 'credit',
            'balance', 'transaction_date', 'student_id'
        ).order_by('transaction_date')  # Order by transaction date ascending

        # Initialize balance dictionary for each student
        student_balances = {}

        # Calculate and set balance for each transaction
        for transaction in data:
            student_id = transaction['student_id']
            # Initialize balance for new student
            if student_id not in student_balances:
                student_balances[student_id] = 0

            # Calculate current balance
            current_balance = student_balances[student_id] + transaction['debit'] - transaction['credit']
            transaction['balance'] = current_balance

            # Update balance for the student
            student_balances[student_id] = current_balance

        response.setStatusCode(status.HTTP_200_OK)
        response.setMessage("RecordTransactions Found")
        response.setEntity(list(data))  # Convert to list to be JSON serializable
        return Response(response.toDict(), status=response.status)
