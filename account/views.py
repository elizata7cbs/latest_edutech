from django.http import Http404
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Account
from .serializers import AccountSerializer
from rest_framework import generics, status
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


class AccountListAPIView(APIView):
    @swagger_auto_schema(
        operation_description="List all accounts",
        responses={200: AccountSerializer(many=True)}
    )
    def get(self, request):
        accounts = Account.objects.all()
        serializer = AccountSerializer(accounts, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Create a new account",
        request_body=AccountSerializer,
        responses={201: AccountSerializer()}
    )
    def post(self, request):
        serializer = AccountSerializer(data=request.data)
        try:
            if serializer.is_valid():
                account = serializer.save()
                return Response(AccountSerializer(account).data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Update an existing account",
        request_body=AccountSerializer,
        responses={200: AccountSerializer()}
    )
    def put(self, request, pk):
        account = self.get_object(pk)
        serializer = AccountSerializer(account, data=request.data)
        try:
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Delete an existing account",
        responses={204: "No Content"}
    )
    def delete(self, request, pk):
        account = self.get_object(pk)
        try:
            account.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_object(self, pk):
        try:
            return Account.objects.get(pk=pk)
        except Account.DoesNotExist:
            raise Http404


class AccountBalanceAPIView(generics.RetrieveAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    @swagger_auto_schema(
        operation_description="Get account balance",
        responses={200: openapi.Schema(type=openapi.TYPE_OBJECT, properties={'balance': openapi.Schema(type=openapi.TYPE_NUMBER)})}
    )
    def get(self, request, *args, **kwargs):
        account = self.get_object()
        return Response({'balance': account.balance})


class AccountDebitAPIView(generics.UpdateAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    @swagger_auto_schema(
        operation_description="Debit an account",
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT, properties={'amount': openapi.Schema(type=openapi.TYPE_NUMBER)}),
        responses={200: "Account debited successfully"}
    )
    def put(self, request, *args, **kwargs):
        account = self.get_object()
        amount = request.data.get('amount')

        if amount is None:
            return Response({'error': 'Amount must be provided'}, status=status.HTTP_400_BAD_REQUEST)

        if account.balance < float(amount):
            return Response({'error': 'Insufficient funds'}, status=status.HTTP_400_BAD_REQUEST)

        account.balance -= float(amount)
        account.save()

        return Response({'message': 'Account debited successfully'}, status=status.HTTP_200_OK)
