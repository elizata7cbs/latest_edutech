from django.db import transaction
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response

from allfees.models import FeeCollectionsAll
from allfees.serializers.FeeViewSerializer import FeeViewSerializer
from transactions.models import Transaction


# Create your views here.
class FeeView(viewsets.ModelViewSet):
    serializer_class = FeeViewSerializer
    queryset = FeeCollectionsAll.objects.all()
    # @TODO: implement JWT auth

    def manual_pay_fee(self, request, *args, **kwargs):
        try:
            serializer = FeeViewSerializer(data=request.data)
            if serializer.is_valid():
                with transaction.atomic():
                    tran = serializer.save()
                    Transaction.objects.create(
                        amount=serializer.data['amountPaid'],
                        ref_number="REd4%#3@GF",
                        type="CR",
                        status=1,
                        tran_category=serializer.data['payment_mode']
                    )
                return Response({'message': 'Fees was paid successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Invalid data', 'errors': serializer.errors},
                                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Log the exception (this can be done with proper logging in a real-world scenario)
            print(f"An error occurred: {e}")
            return Response({'message': 'An error occurred', 'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


