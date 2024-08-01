from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from parents.models import Parents
from parents.serializers import ParentsCreateSerializers, ParentsLoginSerializers
from students.models import Students
from utils.Helpers import Helpers
from utils.ApiResponse import ApiResponse


class ParentViewSet(ModelViewSet):
    queryset = Parents.objects.all()

    def get_serializer_class(self):
        if self.action == 'login':
            return ParentsLoginSerializers
        return ParentsCreateSerializers

    @action(detail=False, methods=['POST'], url_path='login', url_name='login')
    def login(self, request):
        serializer = ParentsLoginSerializers(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data.get('username')
            password = serializer.validated_data.get('password')
            helpers = Helpers()
            helpers.log(request)
            if username and password:
                try:
                    parent = Parents.objects.get(username=username)
                    if parent.check_password(password):
                        parent_data = ParentsCreateSerializers(parent).data
                        response = ApiResponse()
                        response.setStatusCode(status.HTTP_200_OK)
                        response.setMessage("Login successful")
                        response.setEntity(parent_data)
                        return Response(response.toDict(), status=response.status)
                    else:
                        response = ApiResponse()
                        response.setStatusCode(status.HTTP_400_BAD_REQUEST)
                        response.setMessage("Incorrect login credentials")
                        return Response(response.toDict(), status=200)
                except Parents.DoesNotExist:
                    response = ApiResponse()
                    response.setStatusCode(status.HTTP_400_BAD_REQUEST)
                    response.setMessage("Incorrect login credentials")
                    return Response(response.toDict(), status=200)
            else:
                response = ApiResponse()
                response.setStatusCode(status.HTTP_400_BAD_REQUEST)
                response.setMessage("Username and password are required")
                return Response(response.toDict(), status=response.status)
        else:
            response = ApiResponse()
            response.setStatusCode(status.HTTP_400_BAD_REQUEST)
            response.setMessage("Invalid data")
            return Response(response.toDict(), status=response.status)

    def create(self, request):
        serializer = ParentsCreateSerializers(data=request.data)
        if serializer.is_valid():
            parent = serializer.save()
            response_data = ParentsCreateSerializers(parent).data
            response = ApiResponse()
            response.setStatusCode(status.HTTP_201_CREATED)
            response.setMessage("Parent created successfully")
            response.setEntity(response_data)
            return Response(response.toDict(), status=response.status)
        else:
            response = ApiResponse()
            response.setStatusCode(status.HTTP_400_BAD_REQUEST)
            response.setMessage("Invalid data")
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

    def makepyments(self, request):
        response = ApiResponse()  # Initialize your custom API response
        helper = Helpers()  # Initialize a helper object, presumably containing utility methods
        print(request.data)  # Print the incoming request data to the console for debugging

        # Unique Id
        # uniqueid = helper.generateUniqueId(schoolCode, admNo)

        # Actual student saving
        FeePayments.objects.create(

            uniqueid=request.data.get('uniqueid'),
            amount=request.data.get('amount'),
            paymentmethod=request.data.get('paymentmethod '),

        )

        return Response(response.toDict(), status=response.status)

    def parent_students(request, parent_id):
        try:
            parent = Parents.objects.get(id=parent_id)
            students = parent.get_students()
            # Serialize the students data if needed
            serialized_students = [{'id': student.id, 'name': student.firstName} for student in students]
            return Response({'students': serialized_students})
        except Parents.DoesNotExist:
            return Response({'error': 'Parent not found'}, status=404)
