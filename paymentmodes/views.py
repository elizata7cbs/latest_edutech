from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response

from paymentmodes.models import PaymentModes
from paymentmodes.serializers import PaymentModesSerializers
from utils.ApiResponse import ApiResponse


# Create your views here.

class PaymentModesView(viewsets.ModelViewSet):
    queryset = PaymentModes.objects.all()
    serializer_class = PaymentModesSerializers

    def list(self, request, *args, **kwargs):
        response = ApiResponse()
        data = list(PaymentModes.objects.all().values())
        response.setStatusCode(status.HTTP_200_OK)
        response.setMessage("Found")
        response.setEntity(data)
        return Response(response.toDict(), status=response.status)

    def create(self, request, *args, **kwargs):
        response = ApiResponse()
        PaymentModesData = PaymentModesSerializers(data=request.data)

        if not PaymentModesData.is_valid():
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "Please fill in the details correctly.", "status": status_code}, status_code)

        # Check if the email is already in use
        name = request.data.get("name")
        existingpaymentmode = PaymentModes.objects.filter(name=name).first()

        if existingpaymentmode:
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "PaymentMode  already exists.", "status": status_code}, status_code)

        # If email is not in use, save the new customer
        PaymentModesData.save()
        response.setStatusCode(status.HTTP_201_CREATED)
        response.setMessage("PaymentModes created")
        response.setEntity(request.data)
        return Response(response.toDict(), status=response.status)

    def update(self, request, *args, **kwargs):
        paymentmodes_details = PaymentModes.objects.get(id=kwargs['pk'])
        paymentmodes_serializer_data = PaymentModesSerializers(
            paymentmodes_details, data=request.data, partial=True)
        if paymentmodes_serializer_data.is_valid():
            status_code = status.HTTP_201_CREATED
            return Response({"message": "PaymentModes data updated successfully", "status": status_code})
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "PaymentModes data not found", "status": status_code})

    def destroy(self, request, *args, **kwargs):
        paymentmodesData = PaymentModes.objects.get(id=kwargs['pk'])
        if paymentmodesData:
            paymentmodesData.delete()
            status_code = status.HTTP_200_OK
            return Response({"message": "PaymentModes data deleted Successfully", "status": status_code})

        else:
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "PaymentModes data not found", "status": status_code})
