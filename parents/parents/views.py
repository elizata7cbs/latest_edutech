from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password
from parents.models import Parents
from parents.serializers import ParentsSerializers
from utils.ApiResponse import ApiResponse
from django.contrib.auth import authenticate, login
from django.http import JsonResponse

# Create your views here.

class ParentsView(viewsets.ModelViewSet):
    queryset = Parents.objects.all()
    serializer_class = ParentsSerializers

    def list(self, request, *args, **kwargs):
        response = ApiResponse()
        data = list(Parents.objects.all().values())
        data['password'] = make_password(data['password'])
        response.setStatusCode(status.HTTP_200_OK)
        response.setMessage("Found")
        response.setEntity(data)
        return Response(response.toDict(), status=response.status)

    def create(self, request, *args, **kwargs):
        response = ApiResponse()
        ParentsData = ParentsSerializers(data=request.data)

        if not ParentsData.is_valid():
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "Please fill in the details correctly.", "status": status_code}, status_code)

        # Check if the email is already in use
        checkIdno = request.data.get("parentIdno")
        existingparent = Parents.objects.filter(parentIdno=checkIdno).first()

        if existingparent:
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "Parents  already exists.", "status": status_code}, status_code)

        # If email is not in use, save the new customer
        ParentsData.save()
        response.setStatusCode(status.HTTP_201_CREATED)
        response.setMessage("Parent created")
        response.setEntity(request.data)
        return Response(response.toDict(), status=response.status)

    def destroy(self, request, *args, **kwargs):

        regionData = Parents.objects.filter(id=kwargs['pk'])
        if regionData:
            regionData.delete()
            status_code = status.HTTP_200_OK
            return Response({"message": "Users deleted Successfully", "status": status_code})
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "Users data not found", "status": status_code})

    def update(self, request, *args, **kwargs):
        users_details = Parents.objects.get(id=kwargs['pk'])
        users_serializer_data = ParentsSerializers(
            users_details, data=request.data, partial=True)
        if users_serializer_data.is_valid():
            users_serializer_data.save()
            status_code = status.HTTP_201_CREATED
            return Response({"message": "Users Update Successfully", "status": status_code})
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "Users data Not found", "status": status_code})


    def parent_login(request):
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                # Login successful
                login(request, user)
                # Redirect to a page where parents can make fee payments, view balances, etc.
                return redirect('parent_dashboard')
            else:
                # Login failed
                return Response({"message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({"message": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def parent_login(request):
            # Your login logic here
            return HttpResponse("Parent Login Page")



    def get_fee_balance(self, request, pk):
        parent = self.get_object()
        fee_balance = parent.get_fee_balance()
        return Response({"fee_balance": fee_balance}, status=status.HTTP_200_OK)

    def get_statement(self, request, pk):
        parent = self.get_object()
        statement = parent.get_statement()
        return Response({"statement": statement}, status=status.HTTP_200_OK)

    def get_student_details(self, request, pk):
        parent = self.get_object()
        # Assuming there's a ForeignKey field 'student' in the Parents model linking it to the Student model
        student = parent.student
        student_data = {
            'student_name': student.name,
            'student_grade': student.grade,
            'student_dob': student.date_of_birth,
            # Add more student details as needed
        }
        return Response(student_data, status=status.HTTP_200_OK)

    def get_transaction_history(self, request, pk):
        parent = self.get_object()
        # Your logic to retrieve transaction history
        transaction_history = []  # Implement logic to retrieve transaction history
        return Response(transaction_history, status=status.HTTP_200_OK)
