from django.utils.crypto import get_random_string
from django.views.generic import View
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db.models import Q, Max
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from students.models import Students
from feecategories.models import FeeCategories
from feecollections.models import FeeCollections
from feecollections.serializers import FeeCollectionsSerializers
from datetime import datetime
from utils.ApiResponse import ApiResponse
from rest_framework.views import APIView
from schools.models import Schools
from utils.Helpers import Helpers
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
# from xhtml2pdf import pisa
from django.utils import timezone
import requests
# from utils.Helpers import credit_student_account, record_credit_transaction
# from utils.Helpers import generate_receipt_and_save_payment  # Import the receipt generation function
from decimal import Decimal



class FeeCollectionsView(viewsets.ModelViewSet):
    queryset = FeeCollections.objects.all()
    serializer_class = FeeCollectionsSerializers
    filter_backends = [filters.SearchFilter]
    search_fields = ['studentId__first_name', 'studentId__middle_name', 'studentId__last_name', 'studentId__id',
                     'uniqueid', 'amountPaid', 'payment_date', 'outstanding_balance', 'grade']
    pagination_class = PageNumberPagination
    # authentication_classes = [JSONWebTokenAuthentication, SessionAuthentication]
    # permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        response = ApiResponse()
        data = list(FeeCollections.objects.all().values())
        response.setStatusCode(status.HTTP_200_OK)
        response.setMessage("Found")
        response.setEntity(data)
        return Response(response.toDict(), status=response.status)

    def get_queryset(self):
        queryset = FeeCollections.objects.all()
        search_query = self.request.query_params.get('search')
        sort_by = self.request.query_params.get('sort_by')
        grade = self.request.query_params.get('grade')  # New parameter for grade filter

        if grade:  # Apply grade filter if grade parameter is provided
            queryset = queryset.filter(grade=grade)
        if search_query:
            queryset = queryset.filter(
                Q(studentId__first_name__icontains=search_query) |
                Q(studentId__middle_name__icontains=search_query) |
                Q(studentId__last_name__icontains=search_query) |
                Q(studentId__id__icontains=search_query) |
                Q(uniqueid__icontains=search_query) |
                Q(amountPaid__icontains=search_query) |
                Q(payment_date__icontains=search_query) |
                Q(receipt_number__icontains=search_query) |
                Q(outstanding_balance__icontains=search_query) |
                Q(grade__icontains=search_query)
            )
        if sort_by:
            queryset = queryset.order_by(sort_by)

        return queryset

    @classmethod
    def create_payment(cls, student_id, fee_category, unique_id, payment_info, payment_reference, payment_mode,
                       school_code):
        amount_paid = Decimal(payment_info['amountPaid'])  # Convert to Decimal
        fee_category_amount = Decimal(fee_category.amount)
        outstanding_balance = fee_category_amount - amount_paid

        # Generate a unique receipt number
        receipt_number = Helpers.generate_receipt_number

        # Create the payment instance
        payment = cls(
            studentId=student_id,
            feecategory=fee_category,
            uniqueid=unique_id,
            payment_reference=payment_reference,
            amountPaid=amount_paid,
            outstandingbalance=outstanding_balance,  # Assign numeric value
            grade=payment_info['grade'],
            payment_mode=payment_mode,
            school_code=school_code,
            receipt_number=receipt_number,
        )

        payment.payment_date = payment_info['payment_date']
        payment.save()
        return payment

    def save(self, *args, **kwargs):
        if not self.payment_receipt:
            # Generate a random alphanumeric reference number
            self.payment_reference = get_random_string(length=10)
            super().save(*args, **kwargs)

    def __str__(self):
        return f"Payment for {self.studentId.name} - Category: {self.feecategory.name} - Unique ID: {self.uniqueid} - Amount Paid: {self.amountPaid} - Payment Date: {self.payment_date} - Reference: {self.payment_reference} - Outstanding Balance: {self.outstanding_balance} - Grade: {self.grade} - Receipt Number: {self.receipt_number} - Payment Mode: {self.payment_mode}"


def retrieve_payment_data_from_bank_api():
    # Make a GET request to the bank's API to fetch payment data
    bank_api_url = 'https://bank-api.example.com/data'
    response = requests.get(bank_api_url)

    try:
        response = requests.get(bank_api_url)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)

        if response.status_code == 200:
            payment_data = response.json()

            # Extract required fields from payment data
            student_id = payment_data.get('student_id')
            fee_category = payment_data.get('fee_category')
            unique_id = payment_data.get('unique_id')
            payment_reference = payment_data.get('payment_reference')
            payment_mode = determine_payment_mode(payment_reference)
            school_code = payment_data.get('school_code')
            amount_paid = payment_data.get('amountPaid')
            outstanding_balance = payment_data.get('outstandingbalance')
            grade = payment_data.get('grade')
            payment_date = payment_data.get('payment_date')

            outstanding_balance = fee_category - amount_paid
            extracted_fields = {
                'student_id': student_id,
                'fee_category': fee_category,
                'unique_id': unique_id,
                'payment_reference': payment_reference,
                'payment_mode': payment_mode,
                'school_code': school_code,
                'payment_info': {
                    'amountPaid': amount_paid,
                    'outstandingbalance': outstanding_balance,
                    'grade': grade,
                    'payment_date': payment_date
                }
            }

            return extracted_fields
        else:
            # Handle unexpected status code from the bank's API
            print(f"Unexpected status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        # Handle any network-related errors (e.g., connection timeout, DNS resolution error)
        print(f"Error connecting to the bank API: {e}")
        return None


def determine_payment_mode(payment_reference):
    # Your logic to determine the payment mode based on the payment reference
    if 'MPS' in payment_reference.upper():
        return 'Mobile Wallet (MPESA)'
    elif 'airtelmoney' in payment_reference.upper():
        return 'Mobile Wallet (Airtel Money)'
    elif 'T-Kash' in payment_reference.upper():
        return 'Mobile Wallet (Telkom Kash)'
    elif 'APP' in payment_reference.upper():
        return 'Equity Bank Mobile App'
    elif 'EAZZY-MMONEY' in payment_reference.upper() or '/STK/' in payment_reference.upper():
        return 'Equitel'
    elif 'NBK' in payment_reference.upper():
        return 'National Bank of Kenya'
    elif 'KCB' in payment_reference.upper():
        return 'Kenya Commercial Bank (KCB)'
    elif 'COOP' in payment_reference.upper():
        return 'Cooperative Bank of Kenya'
    elif 'STANBIC' in payment_reference.upper():
        return 'Stanbic Bank'
    else:
        return 'CASH DEPOSIT'  # Default if payment mode cannot be determined


def process_payment_and_create_record():
    # Retrieve payment data from bank API
    payment_data = retrieve_payment_data_from_bank_api()
    payment_mode = determine_payment_mode(payment_data.get('payment_reference', ''))

    try:
        student = Students.objects.get(id=payment_data['student_id'])
        fee_category = FeeCategories.objects.get(id=payment_data['fee_category'])
    except (Students.DoesNotExist, FeeCategories.DoesNotExist):
        return Response({"error": "Invalid student or fee category"}, status=400)

    # Extract required fields from payment data
    required_fields = {
        'student_id': payment_data['student_id'],
        'fee_category': payment_data['fee_category'],
        'unique_id': payment_data['unique_id'],
        'payment_reference': payment_data['payment_reference'],
        'payment_mode': payment_data['payment_mode'],
        'school_code': payment_data['school_code'],
        'payment_info': {
            'amountPaid': payment_data['amountPaid'],
            'outstandingbalance': payment_data['outstandingbalance'],
            'grade': payment_data['grade'],
            'payment_date': payment_data['payment_date'],
        }
    }

    # Create a payment record in the feecollections app
    payment = FeeCollections.create_payment(**required_fields)
    amount_paid = payment_data['amountPaid']
    student.outstanding_balance -= amount_paid
    student.save()

    credit_student_account = Helpers.credit_student_account
    record_credit_transaction = Helpers.record_credit_transaction


    return Response({'amount_paid': amount_paid}, status=status.HTTP_201_CREATED)
    return payment


def calculate_total_fee(self, request):  # Add request parameter if needed
    fee_payments = FeeCollections.objects.all()
    amount_paid = sum(float(fee.amount_paid) for fee in fee_payments)

    return Response({
        'Fee Payments': amount_paid,

    })


class StatementView(APIView):
    pagination_class = PageNumberPagination

    def get(self, request, *args, **kwargs):
        search_param = request.query_params.get('search', '')
        sort_by = request.query_params.get('sort_by', '')

        # Define the columns to search within
        columns = ['id', 'studentId__name', 'feecategory__name', 'uniqueid', 'amountPaid', 'payment_date',
                   'payment_reference', 'outstanding_balance', 'grade', 'payment_mode']

        # Create filters for each column to perform case-insensitive partial match
        filters = Q()
        for column in columns:
            filters |= Q(**{f"{column}__icontains": search_param})

        # Applying filters to the queryset
        fee_collections_data = FeeCollections.objects.filter(filters)

        # Serialize fee payment data
        serializer = FeeCollectionsSerializers(fee_collections_data, many=True)

        # Extract receipt numbers from fee payment data
        receipt_numbers = fee_collections_data.values_list('receipt_number', flat=True)

        # Return response with serialized fee payment data and receipt numbers
        return Response({
            'fee_collections_data': serializer.data,
            'receipt_numbers': receipt_numbers
        })


class ReceiptView(View):
    def get(self, request, receipt_number):
        try:
            fee_payment = FeeCollections.objects.get(receipt_number=receipt_number)

            # Render receipt template with fee payment data
            template = get_template('receipt.html')
            context = {'fee_payment': fee_payment}
            html = template.render(context)

            # Generate PDF
            pdf = self.render_to_pdf(html)

            # Return PDF as response
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = f'receipt_{receipt_number}.pdf'
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response

        except FeeCollections.DoesNotExist:
            return HttpResponse(status=404)

    def render_to_pdf(self, html):
        # Generate PDF from HTML content
        pdf = pisa.CreatePDF(html, dest=None)
        return pdf.dest.getvalue()

    def share_receipt_via_email(self, receipt_number, recipient_email):
        # Logic to send email with receipt attached
        pass

    def share_receipt_via_whatsapp(self, receipt_number, recipient_number):
        # Logic to send receipt via WhatsApp
        pass

    def share_receipt_via_telegram(self, receipt_number, recipient_username):
        # Logic to send receipt via Telegram
        pass


class FilterFeeCollections(APIView):
    def get(self, request, *args, **kwargs):
        # Get the search parameter from query parameters
        search_param = request.query_params.get('search', '')

        # Define the columns to search within
        columns = ['id', 'studentId__name', 'feecategory__name', 'uniqueid', 'amountPaid', 'payment_date',
                   'payment_reference', 'outstanding_balance', 'grade', 'receipt_number', 'payment_mode']

        # Create filters for each column to perform case-insensitive partial match
        filters = Q()
        for column in columns:
            filters |= Q(**{f"{column}__icontains": search_param})

        # Applying filters to the queryset
        fee_collections_data = FeeCollections.objects.filter(filters)

        # Construct the response based on whether records are found or not
        if fee_collections_data.exists():  # Check if any fee payments match the search criteria
            response_data = {
                "message": "Records retrieved",
                "status_code": status.HTTP_200_OK,
                "data": list(fee_collections_data.values())
            }
        else:
            response_data = {
                "message": "No records found for the provided search criteria",
                "status_code": status.HTTP_404_NOT_FOUND,
                "data": []
            }

        return Response(response_data)
