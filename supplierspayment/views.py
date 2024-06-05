from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response

from suppliers.models import Suppliers, SuppliersAccount
from supplierspayment.models import SuppliersPayment
from supplierspayment.serializers import SuppliersPaymentSerializers
from utils.ApiResponse import ApiResponse
from utils.Helpers import Helpers


# Create your views here.
class SuppliersPaymentView(viewsets.ModelViewSet):
    queryset = SuppliersPayment.objects.all()
    serializer_class = SuppliersPaymentSerializers

    # authentication_classes = [JSONWebTokenAuthentication, SessionAuthentication, BasicAuthentication]
    # permission_classes = [IsAuthenticated]

    def pay_supplier(self, request):
        # Instantiate the Helpers class
        helper = Helpers()

        # Retrieve the data sent with the request
        supplier_id = request.data.get('student')
        amount_paid = request.data.get('amount_paid')
        payment_date = request.data.get('payment_date')
        paymentmode = request.data.get('paymentmode')

        reference = request.data.get('reference')

        # Retrieve the student object
        suppliers = Suppliers.objects.get(id=supplier_id)

        # generate reference
        # helper.generate_reference(payment_date)

        # Create a fee collection entry
        SuppliersPayment.objects.create(
            supplier=suppliers,
            amount_paid=amount_paid,
            paymentmode=paymentmode,
            payment_date=payment_date,
            reference=reference,
        )

        # Credit the student account
        helper.credit_supplier_account(supplier_id)
        # helper.record_credit_transaction(supplier_id)

        return Response({'amount_paid': amount_paid}, status=status.HTTP_201_CREATED)

    def list_supplier_account(request):
        response = ApiResponse()

        try:
            # Query all supplier accounts
            supplier_accounts = SuppliersAccount.objects.all()

            # List to store supplier account info
            supplier_accounts_info = []

            # Iterate through each supplier account
            for account in supplier_accounts:
                # Get the associated supplier
                supplier = account.supplier

                # Extract necessary information
                supplier_info = {
                    'supplier_name': supplier.businessName,
                    'supplier_id_no': supplier.supplieridNO,
                    'debit': account.debit,
                    'credit': account.credit,
                    'balance': account.balance,
                }

                # Append supplier account info to the list
                supplier_accounts_info.append(supplier_info)

            # Set response data
            response.setStatusCode(status.HTTP_200_OK)
            response.setMessage("Supplier accounts retrieved successfully")
            response.setEntity(supplier_accounts_info)

        except Exception as e:
            # Handle exceptions
            response.setStatusCode(status.HTTP_500_INTERNAL_SERVER_ERROR)
            response.setMessage("Error occurred while retrieving supplier accounts")
            response.setEntity(str(e))

        # Return response
        return Response(response.toDict(), status=response.status)
