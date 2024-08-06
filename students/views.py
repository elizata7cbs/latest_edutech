import os
import time
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import AllowAny
from edutech_payment_engine import settings
from parents.models import Parents
from schools.models import Schools
from students.models import Students
from students.serializers import StudentsSerializers
from studentsparents.models import StudentsParents
from utils.ApiResponse import ApiResponse
from django.db.models import Q
from utils.Helpers import Helpers
from django.core.files.storage import FileSystemStorage
from edutech_payment_engine.settings import MEDIA_URL
from rest_framework.pagination import PageNumberPagination
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

class StudentsView(viewsets.ModelViewSet):
    queryset = Students.objects.all()
    serializer_class = StudentsSerializers
    def list(self, request, *args, **kwargs):
        response = ApiResponse()
        data = list(Students.objects.all().values())
        response.setStatusCode(status.HTTP_200_OK)
        response.setMessage("Found")
        response.setEntity(data)
        return Response(response.toDict(), status=response.status)

    def create(self, request, *args, **kwargs):
        response = ApiResponse()
        StudentsData = StudentsSerializers(data=request.data)

        if not StudentsData.is_valid():
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "Please fill in the details correctly.", "status": status_code}, status_code)

        student = Students(
            firstName=request.data.get('firstName'),
            middleName=request.data.get('middleName'),
            lastName=request.data.get('lastName'),
            studentGender=request.data.get('studentGender'),
            dob=request.data.get('dob'),
            healthStatus=request.data.get('healthStatus'),
            grade=request.data.get('grade'),
            stream=request.data.get('stream'),
            schoolStatus=request.data.get('schoolStatus'),
            dormitory=request.data.get('dormitory'),
            parentID=request.data.get('parentID'),
            schoolCode=request.data.get('schoolCode'),
            urls=request.data.get('urls', [])
        )
        student.save()

        parent = Parents.objects.get(id=request.data.get('parentID'))

        StudentsParents.objects.create(
            parentID=parent,
            studentID=student
        )

        response.setMessage("Student created successfully")
        response.setStatusCode(200)

        return Response(response.toDict(), 200)

    def destroy(self, request, *args, **kwargs):

        studentData = Students.objects.filter(id=kwargs['pk'])
        if studentData:
            studentData.delete()

            status_code = status.HTTP_200_OK
            return Response({"message": "Student deleted Successfully", "status": status_code})
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "Student data not found", "status": status_code})

    def update(self, request, *args, **kwargs):

        students_details = Students.objects.get(id=kwargs['pk'])
        students_serializer_data = StudentsSerializers(students_details, data=request.data, partial=True)
        if students_serializer_data.is_valid():
            students_serializer_data.save()
            status_code = status.HTTP_201_CREATED
            return Response({"message": "Student Updated Successfully", "status": status_code})
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "Student data Not found", "status": status_code})

    class FeeTransaction:
        pass

    def filter_students(self, request, *args, **kwargs):
        columns = ['admNumber', 'id', 'stream', ]
        search_param = kwargs.get('str', '')

        filters = Q()
        for column in columns:
            filters |= Q(**{f"{column}__icontains": search_param})

        students_data = Students.objects.filter(filters)

        if students_data.exists():
            response = {
                "message": "Records retrieved",
                "status_code": 200,
                "data": list(students_data.values())
            }
        else:
            response = {
                "message": "No records found for the provided search criteria",
                "status_code": 404,
                "data": []
            }

        return Response(response, status=status.HTTP_200_OK if students_data.exists() else status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['POST'])
    def createStudent(self, request):
        response = ApiResponse()
        helper = Helpers()
        print(request.data)

        schoolCode = request.data.get('schoolCode')
        admNo = request.data.get('admNumber')

        urls = []
        uniqueid = helper.generateUniqueId(schoolCode, admNo)
        if request.FILES:
            print("File found..................")
            uploaded_files = request.FILES

            upload_dir = os.path.join(MEDIA_URL, "students")

            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)

            for uploaded_file_name, uploaded_file in uploaded_files.items():
                print(uploaded_file_name)
                fs = FileSystemStorage(location=upload_dir)
                filename = fs.save(uploaded_file_name, uploaded_file)

                uploaded_file_path = os.path.join(upload_dir, filename)

                timestamp = str(int(time.time() * 1000))
                file_name, file_extension = os.path.splitext(uploaded_file_name)
                new_filename = f"{uniqueid}_{timestamp}{file_extension}"
                new_file_path = os.path.join(upload_dir, new_filename)
                os.rename(uploaded_file_path, new_file_path)

                domain = request.get_host()
                protocol = 'https://' if request.is_secure() else 'http://'
                media_url = f"{protocol}{domain}/{MEDIA_URL}"
                file_url = media_url + 'students/' + new_filename
                urls.append(file_url)

        print(urls)

        student = Students.objects.create(
            uniqueId=uniqueid,
            admNumber=request.data.get('admNumber'),
            firstName=request.data.get('firstName'),
            middleName=request.data.get('middleName'),
            lastName=request.data.get('lastName'),
            studentGender=request.data.get('studentGender'),
            dob=request.data.get('dob'),
            dateOfAdmission=request.data.get('dateOfAdmission'),
            healthStatus=request.data.get('healthStatus'),
            grade=request.data.get('grade'),
            stream=request.data.get('stream'),
            schoolStatus=request.data.get('schoolStatus'),
            dormitory=request.data.get('dormitory'),
            parentID=request.data.get('parentID'),
            upiNumber=request.data.get('upiNumber'),
            urls=urls
        )

        parent = Parents.objects.get(id=request.data.get('parentID'))

        StudentsParents.objects.create(
            parentID=parent,
            studentID=student
        )

        response.setMessage("Student created successfully")
        response.setStatusCode(200)

        return Response(response.toDict(), 200)

    @action(detail=False, methods=['GET'])
    @permission_classes([AllowAny])
    def check_student_exists(self, request):
        admNumber = request.query_params.get('admNumber')
        schoolCode = request.query_params.get('schoolCode')

        if not admNumber or not schoolCode:
            return Response({
                "message": "admNumber and schoolCode are required parameters",
                "status_code": status.HTTP_400_BAD_REQUEST
            }, status=status.HTTP_400_BAD_REQUEST)

        student_exists = Students.objects.filter(admNumber=admNumber, schoolCode=schoolCode).exists()

        return Response({
            "student_exists": student_exists,
            "status_code": status.HTTP_200_OK
        }, status=status.HTTP_200_OK)
