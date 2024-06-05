from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets, status, filters
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from paymentgroups.models import PaymentGroups
from paymentgroups.serializers import PaymentGroupsSerializers
from utils.ApiResponse import ApiResponse
from rest_framework import viewsets, filters
from .models import PaymentGroups
from .serializers import PaymentGroupsSerializers
from rest_framework.response import Response
from rest_framework.decorators import action


# Create your views here.

class PaymentGroupsView(viewsets.ModelViewSet):
    queryset = PaymentGroups.objects.all()
    serializer_class = PaymentGroupsSerializers

    # pagination_class = PageNumberPagination
    # authentication_classes = [JSONWebTokenAuthentication, SessionAuthentication]
    # permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        response = ApiResponse()
        data = list(PaymentGroups.objects.all().values())
        response.setStatusCode(status.HTTP_200_OK)
        response.setMessage("Found")
        response.setEntity(data)
        return Response(response.toDict(), status=response.status)

    def create(self, request, *args, **kwargs):
        response = ApiResponse()
        PaymentGroupsData = PaymentGroupsSerializers(data=request.data)

        if not PaymentGroupsData.is_valid():
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "Please fill in the details correctly.", "status": status_code}, status_code)

        # Check if the email is already in use
        # checkIdno = request.data.get("parentIdno")
        # existingparent = PaymentGroups.objects.filter(parentIdno=checkIdno).first()
        #
        # if existingparent:
        #     status_code = status.HTTP_400_BAD_REQUEST
        #     return Response({"message": "PaymentGroups  already exists.", "status": status_code}, status_code)

        # If email is not in use, save the new customer
        PaymentGroupsData.save()
        response.setStatusCode(status.HTTP_201_CREATED)
        response.setMessage("FeeCategory created")
        response.setEntity(request.data)
        return Response(response.toDict(), status=response.status)

    def destroy(self, request, *args, **kwargs):

        regionData = PaymentGroups.objects.filter(id=kwargs['pk'])
        if regionData:
            regionData.delete()
            status_code = status.HTTP_200_OK
            return Response({"message": "paymentgroups deleted Successfully", "status": status_code})
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "paymentgroups data not found", "status": status_code})

    def update(self, request, *args, **kwargs):
        users_details = PaymentGroups.objects.get(id=kwargs['pk'])
        users_serializer_data = PaymentGroupsSerializers(
            users_details, data=request.data, partial=True)
        if users_serializer_data.is_valid():
            users_serializer_data.save()
            status_code = status.HTTP_201_CREATED
            return Response({"message": "paymentgroups Update Successfully", "status": status_code})
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "paymentgroups data Not found", "status": status_code})

    class PaymentGroupsView(viewsets.ModelViewSet):
        queryset = PaymentGroups.objects.all()
        serializer_class = PaymentGroupsSerializers
        filter_backends = [filters.SearchFilter]
        search_fields = ['name', 'datePosted']  # Specify fields for searching by name or date posted

        def filter_queryset(self, queryset):
            params = self.request.query_params
            filters = {}

            # Filter by status
            status_param = params.get('status')
            if status_param is not None:
                filters['status'] = status_param

            # Filter by name
            name_param = params.get('name')
            if name_param:
                filters['name__icontains'] = name_param

            # Filter by datePosted
            date_param = params.get('datePosted')
            if date_param:
                filters['datePosted'] = date_param

            # Add more filtering criteria as needed

            return queryset.filter(**filters)

        @action(detail=False, methods=['get'], url_path='filter')
        def filter_groups(self, request, *args, **kwargs):
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
