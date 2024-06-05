from rest_framework import viewsets, status
from rest_framework.response import Response
# from notifications.models import Notifications
# from notifications.serializers import NotificationsSerializers
from utils.ApiResponse import ApiResponse

class NotificationsView(viewsets.ModelViewSet):
    queryset = Notifications.objects.all()
    # serializer_class = NotificationsSerializers

    def list(self, request, *args, **kwargs):
        response = ApiResponse()
        notifications_data = self.queryset.values()
        response.setStatusCode(status.HTTP_200_OK)
        response.setMessage("Found")
        response.setEntity(list(notifications_data))
        return Response(response.toDict(), status=response.status)

    def create(self, request, *args, **kwargs):
        response = ApiResponse()
        # NotificationsData = NotificationsSerializers(data=request.data)

        if not NotificationsData.is_valid():
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "Please fill in the details correctly.", "status": status_code}, status_code)

        # Check if the id is already in use
        checkId = request.data.get("parentid")
        existing_notification = Notifications.objects.filter(id=checkId).first()

        if existing_notification:
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "Notification already exists.", "status": status_code}, status_code)

        # If id is not in use, save the new notification
        NotificationsData.save()
        response.setStatusCode(status.HTTP_201_CREATED)
        response.setMessage("Notification created")
        response.setEntity(request.data)
        return Response(response.toDict(), status=response.status)



    def destroy(self, request, *args, **kwargs):
        notification_data = self.get_object()
        if notification_data:
            notification_data.delete()
            status_code = status.HTTP_200_OK
            return Response({"message": "Notification deleted successfully", "status": status_code})
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "Notification data not found", "status": status_code})

    def update(self, request, *args, **kwargs):
        notification_instance = self.get_object()
        notification_serializer_data = NotificationsSerializers(
            notification_instance, data=request.data, partial=True)
        if notification_serializer_data.is_valid():
            notification_serializer_data.save()
            status_code = status.HTTP_201_CREATED
            return Response({"message": "Notification updated successfully", "status": status_code})
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "Notification data not found", "status": status_code})
