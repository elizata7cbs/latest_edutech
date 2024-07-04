from rest_framework import status, permissions, authentication
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import ExpensePaymentSerializer
from .models import InsufficientFundsError, NoLinkedAccountError, ExpensePayment
import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class ExpensePaymentAPIView(APIView):
    # authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=ExpensePaymentSerializer,
        responses={
            201: openapi.Response('Payment initiated successfully', ExpensePaymentSerializer),
            400: 'Validation Error',
            503: 'Service Unavailable',
            500: 'Internal Server Error'
        }
    )
    def post(self, request):
        serializer = ExpensePaymentSerializer(data=request.data)
        if serializer.is_valid():
            try:
                payment_destination = serializer.validated_data['payment_destination']
                source_account = serializer.validated_data['source_account']
                destination_account = serializer.validated_data['destination_account']

                payment = serializer.save()

                payment_handlers = {
                    'Bank': self.handle_bank_payment,
                    'M-Pesa': self.handle_mpesa_payment
                }
                handler = payment_handlers.get(payment_destination)
                if handler:
                    return handler(payment, source_account, destination_account)
                else:
                    logger.warning(f"Invalid payment destination: {payment_destination}")
                    return Response({"detail": "Invalid payment destination"}, status=status.HTTP_400_BAD_REQUEST)
            except (InsufficientFundsError, NoLinkedAccountError) as e:
                logger.error(f"Payment error: {e}")
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        logger.error(f"Validation errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def handle_bank_payment(self, payment, source_account, destination_account):
        return self._handle_payment(payment, {
            "amount": float(payment.amount_paid),  # Convert Decimal to float
            "currency": payment.expense.currency,
            "source_account": source_account,
            "destination_account": destination_account
        }, "Bank-to-bank payment", settings.JENGA_BANK_TO_BANK_URL)

    def handle_mpesa_payment(self, payment, source_account, destination_account):
        return self._handle_payment(payment, {
            "amount": float(payment.amount_paid),  # Convert Decimal to float
            "currency": payment.expense.currency,
            "phone_number": source_account,
            "account_number": destination_account
        }, "Bank-to-M-Pesa payment", settings.JENGA_BANK_TO_MOBILE_URL)

    def _handle_payment(self, payment, payload, payment_type, url):
        try:
            headers = {
                "Authorization": f"Bearer {self.get_access_token()}",
                "Content-Type": "application/json"
            }

            response = requests.post(url, json=payload, headers=headers, timeout=10)

            if response.status_code == 200:
                logger.info(f"{payment_type} initiated successfully: {response.json()}")
                return Response({"detail": f"{payment_type} initiated successfully"}, status=status.HTTP_201_CREATED)
            else:
                logger.error(f"Failed {payment_type}: {response.text}")
                return Response({"detail": f"Failed to initiate {payment_type}"}, status=status.HTTP_400_BAD_REQUEST)
        except requests.RequestException as e:
            logger.error(f"{payment_type} request exception: {e}")
            return Response({"detail": "Service unavailable. Please try again later."},
                            status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            logger.error(f"Unhandled exception during {payment_type}: {e}")
            return Response({"detail": "An error occurred. Please try again later."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_access_token(self):
        # Fetch the token using client credentials
        url = settings.JENGA_BANK_TO_BANK_URL
        data = {
            "client_id": settings.JENGA_CLIENT_ID,
            "client_secret": settings.JENGA_CLIENT_SECRET,
            "grant_type": "client_credentials"
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            return response.json().get("access_token")
        else:
            logger.error(f"Failed to fetch access token: {response.text}")
            raise Exception("Failed to fetch access token")
