import os
import django
from academics.models import AcademicYear
from academics.serializers import AcademicYearSerializers
from django.utils.dateparse import parse_date

# Manually configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edutech_payment_engine.settings')
django.setup()
# from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.pagination import PageNumberPagination
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from utils.ApiResponse import ApiResponse
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from utils.Helpers import Helpers


class AcademicYearView(viewsets.ModelViewSet):
    queryset = AcademicYear.objects.all()

    serializer_class = AcademicYearSerializers
    filter_backends = [filters.SearchFilter]
    # search_fields = ['name', 'description', 'status']
    pagination_class = PageNumberPagination

    # authentication_classes = [JSONWebTokenAuthentication, SessionAuthentication]
    # permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        response = ApiResponse()
        data = list(AcademicYear.objects.all().values())
        response.setStatusCode(status.HTTP_200_OK)
        response.setMessage("Found")
        response.setEntity(data)
        return Response(response.toDict(), status=response.status)



    # def create(self, request, *args, **kwargs):
    #     response = ApiResponse()
    #     AcademicYearData = AcademicYearSerializers(data=request.data)
    #
    #     if not AcademicYearData.is_valid():
    #         status_code = status.HTTP_400_BAD_REQUEST
    #         return Response({"message": "Please fill in the details correctly.", "status": status_code}, status_code)
    #
    #     # If email is not in use, save the new customer
    #     AcademicYearData.save()
    #     response.setStatusCode(status.HTTP_201_CREATED)
    #     response.setMessage("FeeCategory created")
    #     response.setEntity(request.data)
    #     return Response(response.toDict(), status=response.status)

    def destroy(self, request, *args, **kwargs):

        regionData = AcademicYear.objects.filter(id=kwargs['pk'])
        if regionData:
            regionData.delete()
            status_code = status.HTTP_200_OK
            return Response({"message": "Users deleted Successfully", "status": status_code})
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "Users data not found", "status": status_code})

    def update(self, request, *args, **kwargs):
        users_details = AcademicYear.objects.get(id=kwargs['pk'])
        users_serializer_data = AcademicYearSerializers(
            users_details, data=request.data, partial=True)
        if users_serializer_data.is_valid():
            users_serializer_data.save()
            status_code = status.HTTP_201_CREATED
            return Response({"message": "Users Update Successfully", "status": status_code})
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "Users data Not found", "status": status_code})

    def deactivate(self, request, *args, **kwargs):
        # Deactivate a fee category
        instance = self.get_object()
        instance.status = 0
        instance.save()
        return Response({"message": "Fee category deactivated successfully"}, status=status.HTTP_200_OK)

    def filter_queryset(self, queryset):
        params = self.request.query_params
        filters = {}

        # Filter by name
        name_param = params.get('name')
        if name_param:
            filters['name__icontains'] = name_param

        # Filter by datePosted
        date_param = params.get('dateCreated')
        if date_param:
            filters['datePosted'] = date_param

        # Filter by status
        status_param = params.get('status')
        if status_param is not None:
            filters['status'] = status_param

        return queryset.filter(**filters)

    def createAcademicYear(self, request):
        helper = Helpers()
        response = ApiResponse()

        academic_year_name = request.data.get('academic_year_name')
        start_date_str = request.data.get('start_date')
        end_date_str = request.data.get('end_date')
        grade = request.data.get('grade')

        # Function to parse date and handle errors
        def parse_date_string(date_str):
            try:
                date = parse_date(date_str)
                if not date:
                    raise ValueError
                return date
            except (ValueError, TypeError):
                return None

        start_date = parse_date_string(start_date_str)
        end_date = parse_date_string(end_date_str)

        if not start_date:
            return Response({'start_date': ["Date has wrong format. Use one of these formats instead: YYYY-MM-DD."]},
                            status=status.HTTP_400_BAD_REQUEST)

        if not end_date:
            return Response({'end_date': ["Date has wrong format. Use one of these formats instead: YYYY-MM-DD."]},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            academic_year = AcademicYear.objects.create(
                academic_year_name=academic_year_name,
                start_date=start_date,
                end_date=end_date,
                grade=grade,
            )
            return Response({'Academic_Year': str(academic_year)}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
