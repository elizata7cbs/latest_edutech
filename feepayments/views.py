from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.http import HttpResponse
from django.db import transaction
from .models import FeePayments
from feepayments.serializers import FeePaymentsSerializers
from students.models import Students
from utils.ApiResponse import ApiResponse
from rest_framework.views import APIView



class FeePaymentsView(viewsets.ModelViewSet):
    queryset = FeePayments.objects.all()
    serializer_class = FeePaymentsSerializers
    # authentication_classes = [JSONWebTokenAuthentication, SessionAuthentication, BasicAuthentication]
    # permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        response = ApiResponse()
        data = list(FeePayments.objects.all().values())
        response.setStatusCode(status.HTTP_200_OK)
        response.setMessage("Found")
        response.setEntity(data)
        return Response(response.toDict(), status=response.status)


def create(self, request, *args, **kwargs):
    response = ApiResponse()
    FeePaymentsData = FeePaymentsSerializers(data=request.data)

    if not FeePaymentsData.is_valid():
        status = status.HTTP_400_BAD_REQUEST  # Initialize status here
        return Response({"message": "Please fill in the details correctly."}, status=status)


    # Check if the email is already in use
    checkID = request.data.get("paymentID")
    existingfeepayment = FeePayments.objects.filter(feepaymentID=checkID).first()

    if existingfeepayment:
        status_code = status.HTTP_400_BAD_REQUEST
        return Response({"message": "FeePayment already exists.", "status": status_code}, status_code)

    # If email is not in use, save the new customer
    if FeePaymentsData.is_valid():
       FeePaymentsData.save()
       response.setStatusCode(status.HTTP_201_CREATED)
       response.setMessage("FeePayment created")
       response.setEntity(request.data)
       return Response(response.toDict(), status=status)  # Use the same 'status' variable here
    else:
       return Response(FeePaymentsData.errors, status=status.HTTP_400_BAD_REQUEST)


def destroy(self, request, *args, **kwargs):
    FeePaymentData = FeePayments.objects.filter(id=kwargs['pk'])
    if FeePaymentData:
        FeePaymentData.delete()
        status_code = status.HTTP_200_OK
        return Response({"message": "Feepayment deleted Successfully", "status": status_code})
    else:
        status_code = status.HTTP_400_BAD_REQUEST
        return Response({"message": "Feepayment data not found", "status": status_code})

def update(self, request, *args, **kwargs):
    feepayments_details = FeePayments.objects.get(id=kwargs['pk'])
    feepayments_serializer_data = FeePaymentsSerializers(
        feepayments_details, data=request.data, partial=True)
    if feepayments_serializer_data.is_valid():
        feepayments_serializer_data.save()
        status_code = status.HTTP_201_CREATED
        return Response({"message": "Feepayment Update Successfully", "status": status_code})
    else:
        status_code = status.HTTP_400_BAD_REQUEST
        return Response({"message": "Feepayment data Not found", "status": status_code})

def search(self, request):
    search_query = request.query_params.get('query', '')
    fee_payments = FeePayments.objects.filter(uniqueid__icontains=search_query)
    serializer = FeePaymentsSerializers(fee_payments, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

def retrieve(self, request, pk=None):
    try:
        fee_payment = FeePayments.objects.get(pk=pk)
        serializer = FeePaymentsSerializers(fee_payment)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except FeePayments.DoesNotExist:
        return Response({"message": "FeePayment not found"}, status=status.HTTP_404_NOT_FOUND)

def process_payment(self, payment_amount, payment_date):
    for fee in self.account.fees:
        if not fee.payment_received:
            if payment_amount >= fee.amount:
                fee.payment_received = True
                fee.payment_date = payment_date
                self.account.balance -= fee.amount
                payment_amount -= fee.amount
                if payment_amount > 0:
                    print(f"Excess payment of {payment_amount:.2f} will be carried forward.")
                return
    print(f"Insufficient payment to cover outstanding fees.")
def update_fee_balance(student_id, payment_amount):
    try:
        with transaction.atomic():
            # Retrieve the student and their outstanding fees
            student = Students.objects.get(id=student_id)
            outstanding_fees = FeePayments.objects.filter(studentID=student, payment_received=False)

            # Update the fee balances based on the received payment
            for fee in outstanding_fees:
                if payment_amount >= fee.amountPaid:
                    fee.payment_received = True
                    fee.save()
                    payment_amount -= fee.amountPaid

            # Update the student's balance
            student.update_balance()

            return True, "Payment and balances updated successfully"
    except Exception as e:
        return False, str(e)

def generate_receipt(self, request, pk=None, payment_amount=None, payment_date=None):
    try:
        if pk:
            fee_payment = FeePayments.objects.get(pk=pk)
            payment_amount = fee_payment.amountPaid  # Assuming payment amount stored in the object
            payment_date = fee_payment.payment_date  # Assuming payment date stored in the object
        elif payment_amount is not None and payment_date is not None:
            pass  # Handle case where both payment_amount and payment_date are provided (if needed)
        else:
            return Response({
                "message": "Missing required data. Provide either fee_payment_id or both payment_amount and payment_date"},
                status=status.HTTP_400_BAD_REQUEST)
    except FeePayments.DoesNotExist:
        return Response({"message": "Fee payment not found"}, status=status.HTTP_404_NOT_FOUND)


def _generate_receipt_content(self, fee_payment, payment_amount, payment_date):
    receipt = f"Receipt for: {fee_payment.student.name}\n"
    return receipt


def generate_statement(self, student_id=None):
    try:
        if student_id:
            student = Students.objects.get(pk=student_id)
        else:
            # If student_id not provided, assume current student context
            student = self.current_student  # Assuming you have a way to access the current student

        statement_content = self._generate_statement_content(student)
        response = HttpResponse(statement_content, content_type='text/plain')
        return response

    except Students.DoesNotExist:
        return Response({"message": "Student not found"}, status=status.HTTP_404_NOT_FOUND)


def _generate_statement_content(self, student):
    statement = f"Statement for: {student.name}\n"  # Example placeholder
    return statement