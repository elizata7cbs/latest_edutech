from datetime import datetime, timedelta, timezone, date
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from feeextensions.models import FeeExtensions
from feeextensions.serializers import FeeExtensionsSerializers
from utils.ApiResponse import ApiResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from utils.Helpers import Helpers
from utils.Helpers import calculate_next_due_date
from .forms import FeeExtensionForm
from .models import FeeExtensions
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from users.models import CustomUser
# from notifications import send_notification_to_user, send_notification_to_school_administration

class FeeExtensionsView(viewsets.ModelViewSet):
    queryset = FeeExtensions.objects.all()
    serializer_class = FeeExtensionsSerializers
    # pagination_class = PageNumberPagination
    # authentication_classes = [JSONWebTokenAuthentication, SessionAuthentication, BasicAuthentication]
    # permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        response = ApiResponse()
        data = list(FeeExtensions.objects.all().values())
        response.setStatusCode(status.HTTP_200_OK)
        response.setMessage("Found")
        response.setEntity(data)
        return Response(response.toDict(), status=response.status)

    def create(self, request, *args, **kwargs):
        response = ApiResponse()
        FeeExtensionsData = FeeExtensionsSerializers(data=request.data)

        if not FeeExtensionsData.is_valid():
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "Please fill in the details correctly.", "status": status_code}, status_code)
        FeeExtensionsData.save()
        response.setStatusCode(status.HTTP_201_CREATED)
        response.setMessage("FeeExtension created")
        response.setEntity(request.data)
        return Response(response.toDict(), status=response.status)

    def destroy(self, request, *args, **kwargs):

        regionData = FeeExtensions.objects.filter(id=kwargs['pk'])
        if regionData:
            regionData.delete()
            status_code = status.HTTP_200_OK
            return Response({"message": "FeeExtension deleted Successfully", "status": status_code})
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "FeeExtension data not found", "status": status_code})

    def update(self, request, *args, **kwargs):
        users_details = FeeExtensions.objects.get(id=kwargs['pk'])
        users_serializer_data = FeeExtensionsSerializers(
            users_details, data=request.data, partial=True)
        if users_serializer_data.is_valid():
            users_serializer_data.save()
            status_code = status.HTTP_201_CREATED
            return Response({"message": "FeeExtension Updated Successfully", "status": status_code})
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "FeeExtension data Not found", "status": status_code})

def create_fee_extension(request):
    if request.method == 'POST':
        form = FeeExtensionForm(request.POST)
        if form.is_valid():
            fee_extension = form.save()
            # send_notification_to_user(fee_extension.user)
            # send_notification_to_school_administration(fee_extension.school_code)
            # messages.success(request, 'Fee extension created successfully.')
            return HttpResponseRedirect('/success/')
    else:
        form = FeeExtensionForm()
    return render(request, 'create_fee_extension.html', {'form': form})

def save(self, *args, **kwargs):
    if not self.dueDate and self.end_date:
        self.dueDate = self.end_date
    # Calculate the next due date based on the selected payment frequency
    if self.dueDate and self.dueDate < date.today():
        self.dueDate = calculate_next_due_date(self.dueDate, self.frequency)

    super().save(*args, **kwargs)

def send_reminders():
    # Get fee extensions with due dates approaching
    upcoming_due_date_fee_extensions = FeeExtensions.objects.filter(
        dueDate__lte=timezone.now() + timedelta(days=3)  # Adjust the reminder window as needed
    )
    for fee_extension in upcoming_due_date_fee_extensions:
        user = fee_extension.user
        user_profile = user.profile  # Assuming you have a related profile model linked to the User model

        # Send reminder to user's email
        send_email(user_profile.email, "Reminder: Payment Due",
                   "Dear {}, this is a reminder that your payment is due soon.".format(user.username))

        # Send reminder to user's phone number
        send_sms(user_profile.phone_number, "Reminder: Payment Due")

def send_email(email, subject, message):
    # Implement email sending logic (e.g., using Django's send_mail function)
    pass

def send_sms(phone_number, message):
    # Implement SMS sending logic (e.g., using a third-party service or SMS gateway)
    pass
