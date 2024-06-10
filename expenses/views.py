import logging
from datetime import datetime

import requests
from django.db.models import Sum
from django.http import Http404, JsonResponse
from django.views import View
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from expensetypes.models import ExpenseTypes
from expensetypes.serializers import ExpenseTypesSerializer
from .models import Expenses
from .serializers import ExpensesSerializer, ExpensePaymentSerializer

logger = logging.getLogger(__name__)


class ExpenseListAPIView(APIView):
    @swagger_auto_schema(
        operation_description="List all expenses and display total expenses",
        responses={
            200: openapi.Response(
                description="List of expenses",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "total_expenses": openapi.Schema(type=openapi.TYPE_NUMBER),
                        "expenses": ExpensesSerializer(many=True)
                    }
                )
            )
        }
    )
    def get(self, request):
        try:
            expenses = self.get_queryset()
            logger.debug(f"All expenses: {expenses}")

            total_expenses = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
            logger.debug(f"Total expenses calculated: {total_expenses}")

            serializer = self.get_serializer(expenses, many=True)
            logger.debug(f"Serialized expenses: {serializer.data}")

            return Response({
                "total_expenses": total_expenses,
                "expenses": serializer.data
            })
        except Expenses.DoesNotExist:
            raise Http404
        except Exception as e:
            logger.error(f"Error retrieving expenses: {e}")
            return Response({"detail": "An error occurred while processing the request."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_queryset(self):
        return Expenses.objects.all()

    def get_serializer(self, *args, **kwargs):
        return ExpensesSerializer(*args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new expense",
        request_body=ExpensesSerializer,
        responses={201: ExpensesSerializer()}
    )
    def post(self, request):
        expense_serializer = self.get_serializer(data=request.data)
        if expense_serializer.is_valid():
            expense = expense_serializer.save()
            if request.FILES.get('receipt'):
                expense.receipt = request.FILES['receipt']
                expense.save()
            return Response(expense_serializer.data, status=status.HTTP_201_CREATED)
        else:
            logger.error(f"Validation errors: {expense_serializer.errors}")
            return Response(expense_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExpenseDetailAPIView(APIView):
    def get_object(self, pk):
        try:
            return Expenses.objects.get(pk=pk)
        except Expenses.DoesNotExist:
            raise Http404

    @swagger_auto_schema(
        operation_description="Retrieve an expense by ID",
        responses={200: ExpensesSerializer()}
    )
    def get(self, request, pk):
        expense = self.get_object(pk)
        serializer = ExpensesSerializer(expense)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Update an existing expense",
        request_body=ExpensesSerializer,
        responses={200: ExpensesSerializer()}
    )
    def put(self, request, pk):
        expense = self.get_object(pk)
        serializer = ExpensesSerializer(expense, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Delete an expense by ID",
        responses={204: "No Content"}
    )
    def delete(self, request, pk):
        expense = self.get_object(pk)
        expense.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ExpenseUpdateAPIView(APIView):
    queryset = Expenses.objects.all()
    serializer_class = ExpensesSerializer


class ExpenseTypeUpdateAPIView(APIView):
    queryset = ExpenseTypes.objects.all()
    serializer_class = ExpenseTypesSerializer


class ExpenseStatsView(View):
    @swagger_auto_schema(
        operation_description="Retrieve expense statistics",
        manual_parameters=[
            openapi.Parameter('term', openapi.IN_QUERY, description="Filter by term or semester",
                              type=openapi.TYPE_STRING),
            openapi.Parameter('month', openapi.IN_QUERY, description="Filter by month (e.g., 'January')",
                              type=openapi.TYPE_STRING)
        ]
    )
    def get(self, request):
        term = request.GET.get('term')
        month = request.GET.get('month')
        filters = {}

        if term:
            filters['term'] = term
        if month:
            try:
                filters['datePosted__month'] = datetime.strptime(month, '%B').month
            except ValueError as e:
                logger.error(f"Invalid month value provided: {month}")
                return JsonResponse({'detail': 'Invalid month value provided.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            total_expenses = Expenses.objects.filter(**filters).aggregate(total=Sum('amount'))['total'] or 0
            return JsonResponse({'total_expenses': total_expenses})
        except Exception as e:
            logger.error(f"Error calculating total expenses: {e}")
            return JsonResponse({'detail': 'An error occurred while processing the request.'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ExpensePaymentAPIView(APIView):

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['source', 'destination', 'transfer'],
            properties={
                'source': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'countryCode': openapi.Schema(type=openapi.TYPE_STRING),
                        'name': openapi.Schema(type=openapi.TYPE_STRING),
                        'accountNumber': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                ),
                'destination': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'type': openapi.Schema(type=openapi.TYPE_STRING),
                        'countryCode': openapi.Schema(type=openapi.TYPE_STRING),
                        'name': openapi.Schema(type=openapi.TYPE_STRING),
                        'accountNumber': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                ),
                'transfer': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'type': openapi.Schema(type=openapi.TYPE_STRING),
                        'amount': openapi.Schema(type=openapi.TYPE_STRING),
                        'currencyCode': openapi.Schema(type=openapi.TYPE_STRING),
                        'reference': openapi.Schema(type=openapi.TYPE_STRING),
                        'date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
                        'description': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            }
        ),
        responses={
            '201': "Expense paid successfully via Jenga",
            '400': "Bad Request - Invalid payment method or missing/invalid data",
            '503': "Service Unavailable - Failed to initiate payment via Jenga or unknown error occurred"
        },
        security=[{"BearerAuth": []}],  # Security header for Authorization
        operation_id="InitiateExpensePayment"  # Operation ID
    )
    def post(self, request):
        """
        Post method to handle expense payment.
        """
        serializer = ExpensePaymentSerializer(data=request.data)
        if serializer.is_valid():
            payment_method = serializer.validated_data.get('payment_method')
            if payment_method == 'Jenga':
                return self.handle_jenga_payment(serializer)
            else:
                return Response({"detail": "Invalid payment method"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def handle_jenga_payment(self, serializer):
        try:
            # Extract payment information from serializer
            amount = serializer.validated_data['amount_paid']
            party_a = serializer.validated_data['party_a']
            account_reference = serializer.validated_data['account_reference']
            transaction_description = serializer.validated_data['transaction_description']

            # Call Jenga API to initiate payment
            response = self.initiate_jenga_payment(amount, party_a, account_reference, transaction_description)

            # Handle Jenga API response
            if response.ok:
                # Payment successful
                return Response({"detail": "Expense paid successfully via Jenga"}, status=status.HTTP_201_CREATED)
            else:
                # Payment failed
                error_message = response.json().get('errorMessage', 'Unknown error occurred')
                return Response(
                    {"detail": f"Failed to initiate payment via Jenga: {error_message}"},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
        except Exception as e:
            # Handle exceptions
            logger.error(f"Error during Jenga payment: {e}")
            return Response({"detail": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    def initiate_jenga_payment(self, amount, party_a, account_reference, transaction_description):
        # Jenga API endpoint for initiating payments
        jenga_payment_url = 'https://uat.finserve.africa/v3-apis/transaction-api/v3.0/remittance/internalBankTransfer'

        # Jenga API credentials
        api_key = 'WAH5yH10p0J9V3q+r8sDmZBFG7y/P28/CBzMRFL7eAsRYoKh8OA/o0jqbyp/cRonjWITTBTlFcsPl7HTTqpb0w=='
        api_secret = 'LU48y4cm8VX5aReR3eNlL5O6cb7En1'

        # Construct request payload
        payload = {
            "amount_paid": "",
            "party_a": "sender_phone_number",
            "account_reference": "account_ref_123",
            "transaction_description": "Payment for something",
            "payment_method": "Jenga"
        }

        # Include headers for authentication (e.g., API key)
        headers = {
            'Authorization': f'Bearer {api_key}:{api_secret}',
            'Content-Type': 'application/json'
        }

        # Make HTTP POST request to Jenga API
        response = requests.post(jenga_payment_url, json=payload, headers=headers)

        return response
