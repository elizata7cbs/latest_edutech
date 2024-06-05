import os
import time
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import AllowAny

from edutech_payment_engine import settings
from parents.models import Parents
from schools.models import Schools
from students.models import Students, StudentAccount
from students.serializers import StudentsSerializers
from studentsparents.models import StudentsParents
from studentsschools.models import StudentsSchools
from utils.ApiResponse import ApiResponse
from django.db.models import Q
from utils.Helpers import Helpers
from django.core.files.storage import FileSystemStorage
from edutech_payment_engine.settings import MEDIA_URL
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
    # def create(self, request, *args, **kwargs):
    #     response = ApiResponse()
    #     helper = Helpers()
    #     StudentsData = StudentsSerializers(data=request.data)
    #     uniqueid = helper.generateUniqueId('KSH099', '96758')
    #     print(uniqueid)
    #     if not StudentsData.is_valid():
    #         status_code = status.HTTP_400_BAD_REQUEST
    #         return Response({"message": "Please fill in the details correctly.", "status": status_code}, status_code)
    #
    #
    #
    #     uniqueid = helper.generateUniqueId('KSH099', '96758')
    #     print(uniqueid)
    #     # StudentsData.save()
    #     response.setStatusCode(status.HTTP_201_CREATED)
    #     response.setMessage("Student created")
    #     response.setEntity(request.data)
    #     return Response(response.toDict(), status=response.status)

    def destroy(self, request, *args, **kwargs):

        studentData = Students.objects.filter(id=kwargs['pk'])
        if studentData:
            studentData.delete()
            status_code = status.HTTP_200_OK
            return Response({"message": "Student deleted Successfully", "status": status_code})
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "Student's data not found", "status": status_code})

    def update(self, request, *args, **kwargs):
        students_details = Students.objects.get(id=kwargs['pk'])
        students_serializer_data = StudentsSerializers(
            students_details, data=request.data, partial=True)
        if students_serializer_data.is_valid():
            students_serializer_data.save()
            status_code = status.HTTP_201_CREATED
            return Response({"message": "Student's Update Successfully", "status": status_code})
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "Student's data Not found", "status": status_code})

        class FeeTransaction:
            pass

    def generate_report(self, request):
        try:
            students = Students.objects.all()
            fee_balance_report = []
            fee_payment_report = []

            for student in students:
                # Calculate fee balance for each student
                fee_transactions = FeeTransaction.objects.filter(student=student)
                total_fee_paid = sum(transaction.amount_paid for transaction in fee_transactions)
                fee_balance = student.total_fee - total_fee_paid

                # Generate fee balance report
                fee_balance_report.append({
                    'student_id': student.id,
                    'student_name': student.name,
                    'fee_balance': fee_balance,
                    # Add more fields as needed
                })

                # Generate fee payment report
                fee_payment_report.append({
                    'student_id': student.id,
                    'student_name': student.name,
                    'total_fee_paid': total_fee_paid,
                    # Add more fields as needed
                })

            report_data = {
                'fee_balance_report': fee_balance_report,
                'fee_payment_report': fee_payment_report
            }

            return Response(report_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    class Parent:
        pass



    def filter_students(self, request, *args, **kwargs):
        columns = ['admNumber', 'id']
        search_param = kwargs.get('str', '')

        filters = Q()
        for column in columns:
            filters |= Q(**{f"{column}__icontains": search_param})

        # Applying filters to the queryset
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
    def createStudent(self, request,):
        response = ApiResponse()  # Initialize your custom API response
        helper = Helpers()  # Initialize a helper object, presumably containing utility methods
        print(request.data)  # Print the incoming request data to the console for debugging
        schoolCode = request.data.get('schoolCode')
        admNo = request.data.get('admNumber')

        # Unique Id
        urls = []
        uniqueid = helper.generateUniqueId(schoolCode, admNo)
        if request.FILES:
            print("File found..................")
            uploaded_files = request.FILES

            upload_dir = os.path.join(MEDIA_URL, "students")

            # Create upload directory if it doesn't exist
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)

            for uploaded_file_name, uploaded_file in uploaded_files.items():
                print(uploaded_file_name)
                fs = FileSystemStorage(location=upload_dir)
                filename = fs.save(uploaded_file_name, uploaded_file)

                # Generate URL for the uploaded file
                uploaded_file_path = os.path.join(upload_dir, filename)

                # Rename the file with current milliseconds timestamp
                # Retain the original file extension
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

        # Actual student saving
        Students.objects.create(
            uniqueId=uniqueid,
            admNumber=request.data.get('admNumber'),
            schoolCode=request.data.get('schoolCode'),
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
            parentIdno=request.data.get('parentIdno'),
            schoolID=request.data.get('schoolID'),
            urls=urls
        )

        parent = Parents.objects.get(parentIdno=request.data.get('parentIdno'))
        student = Students.objects.last()

        StudentsParents.objects.create(
            parentIdno=parent,
            studentID=student
        )


        school = Schools.objects.get(id=request.data.get('schoolID'))
        student = Students.objects.last()

        StudentsSchools.objects.create(
            schoolID=school,
            studentID=student
        )

        response.setMessage("Student created successfully")
        response.setStatusCode(200)  # Set the status code of the API response

        return Response(response.toDict(),
                        200)  # Return the API response as a Django Response object with a 200 status code


    @permission_classes([AllowAny])
    def uploadFiles(self, request):
        if request.FILES:
            print("File found..................")
            uploaded_files = request.FILES
            urls = []
            upload_dir = settings.MEDIA_ROOT  # Use MEDIA_ROOT for file uploads

            # Create upload directory if it doesn't exist
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)

            for uploaded_file in uploaded_files.values():  # Access uploaded files using .values()
                uploaded_file = uploaded_files[uploaded_file]
                fs = FileSystemStorage(location=upload_dir)
                filename = fs.save(uploaded_file.name, uploaded_file)

                # Construct URL for the uploaded file
                file_relative_path = os.path.join('uploads', filename)  # Relative path within MEDIA_ROOT
                file_url = os.path.join(settings.MEDIA_URL, file_relative_path)

                # No need to rename the file if it's already unique

                # Append url to the list
                urls.append(file_url)

            return Response({'urls': urls}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'No files found in the request'}, status=status.HTTP_400_BAD_REQUEST)

    def list_student_virtual_account(self, request, *args, **kwargs):
        response = ApiResponse()
        helper = Helpers()

        try:
            # Retrieve all student virtual accounts
            student_accounts = StudentAccount.objects.all()

            # Construct virtual account information for each student
            virtual_accounts_info = []
            for student_account in student_accounts:
                # Retrieve the student's information associated with the virtual account
                student = student_account.student

                # Construct virtual account information with additional fields
                virtual_account_info = {
                    'student_id': student.id,
                    'unique_id': student.uniqueId,
                    'first_name': student.firstName,
                    'debit': student_account.debit,
                    'credit': student_account.credit,
                    'balance': student_account.balance,
                }
                virtual_accounts_info.append(virtual_account_info)

            response.setStatusCode(status.HTTP_200_OK)
            response.setMessage("Found")
            response.setEntity(virtual_accounts_info)
            return Response(response.toDict(), status=response.status)

        except StudentAccount.DoesNotExist:
            # Handle the case where no student virtual accounts exist
            response.setStatusCode(status.HTTP_404_NOT_FOUND)
            response.setMessage("Student virtual accounts not found")
            return Response(response.toDict(), status=response.status)